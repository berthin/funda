"""Main funda scraper module"""
import datetime
import json
import multiprocessing as mp
from typing import List, Optional
from pathlib import Path
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from funda.config.core import config
from funda.preprocess import clean_date_format, preprocess_data
from funda.logging import logger
from funda.utils import find_zip_code


from dataclasses import dataclass
from funda.types import HousingType


@dataclass
class FundaScraper(object):
    area: str = 'Eindhoven'
    want_to: HousingType = HousingType.buy
    page_start: int = 1
    n_pages: int = 1
    find_past: bool = False
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    days_since: Optional[int] = None
    property_type: Optional[str] = None

    def __post_init__(self):
        self.area = self.area.lower().replace(" ", "-")

        self.page_start = max(self.page_start, 1)
        self.n_pages = max(self.n_pages, 1)
        self.page_end = self.page_start + self.n_pages - 1

        # Instantiate along the way
        self.links: List[str] = []
        self.raw_df = pd.DataFrame()
        self.clean_df = pd.DataFrame()
        self.base_url = config.base_url
        self.selectors = config.css_selector

    def __repr__(self):
        return (
            f"FundaScraper(area={self.area}, "
            f"housing_type={self.want_to}, "
            f"n_pages={self.n_pages}, "
            f"page_start={self.page_start}, "
            f"find_past={self.find_past})"
            f"min_price={self.min_price})"
            f"max_price={self.max_price})"
            f"days_since={self.days_since})"
        )

    @property
    def check_days_since(self) -> int:
        """Whether days since complies"""
        if self.find_past:
            raise ValueError("'days_since' can only be specified when find_past=False.")

        if self.days_since in (None, 1, 3, 5, 10, 30):
            return self.days_since

        raise ValueError("'days_since' must be either None, 1, 3, 5, 10 or 30.")

    @staticmethod
    def _create_temporal_directory() -> None:
        tmp_dir = Path("data")
        tmp_dir.mkdir(exist_ok=True, parents=True)
        return tmp_dir

    @staticmethod
    def _get_links_from_one_parent(url: str) -> List[str]:
        """Scrape all the available housing items from one Funda search page."""
        response = requests.get(url, headers=config.header)
        soup = BeautifulSoup(response.text, "lxml")

        script_tag = soup.find_all("script", {"type": "application/ld+json"})[0]
        json_data = json.loads(script_tag.contents[0])
        urls = [item["url"] for item in json_data["itemListElement"]]
        return list(set(urls))

    def fetch_all_links(self) -> None:
        """Find all the available links across multiple pages."""
        logger.info("*** Phase 1: Fetch all the available links from all pages *** ")
        urls = set()
        main_url = self._build_main_query_url()

        for page_index in tqdm(range(self.page_start, self.page_start + self.n_pages + 1)):
            try:
                item_list = self._get_links_from_one_parent(
                    f"{main_url}&search_result={page_index}"
                )
                urls |= set(item_list)
            except IndexError:
                self.page_end = page_index
                logger.warning(f"*** The last available page is {self.page_end} ***")
                break

        self.links = list(urls)
        logger.info(
            f"*** Got all the urls. {len(self.links)} houses found from {self.page_start} to {self.page_end} ***"
        )

    def _build_main_query_url(self) -> str:
        main_url = f"{self.base_url}/zoeken/{self.want_to.to_dutch()}?selected_area=%5B%22{self.area}%22%5D"

        if self.property_type:  # this is important
            property_types = self.property_type.split(",")
            formatted_property_types = ','.join(f"%22{prop_type}%22" for prop_type in property_types)
            main_url += f"&object_type=%5B{formatted_property_types}%5D"

        if self.find_past:
            main_url += f"&availability=%22unavailable%22"

        if self.min_price or self.max_price:
            min_price = self.min_price or ""
            max_price = self.max_price or ""
            main_url += f"&price=%22{min_price}-{max_price}%22"

        if self.days_since:
            main_url += f"&publication_date={self.check_days_since}"

        logger.info(f"*** Main URL: {main_url} ***")
        return main_url

    @staticmethod
    def get_value_from_css(soup: BeautifulSoup, selector: str) -> str:
        """Use CSS selector to find certain features."""
        result = soup.select(selector)
        if not result:
            return "na"
        return result[0].text

    def scrape_one_link(self, link: str) -> List[str]:
        """Scrape all the features from one house item given a link."""

        # Initialize for each page
        response = requests.get(link, headers=config.header)
        soup = BeautifulSoup(response.text, "lxml")

        # Get the value according to respective CSS selectors
        if self.want_to == HousingType.buy:
            list_since_selector = self.selectors.date_list if self.find_past else self.selectors.listed_since
        else:
            list_since_selector = ".fd-align-items-center:nth-child({}) span".format(9 if self.find_past else 7)

        result = [
            link,
            self.get_value_from_css(soup, self.selectors.price),
            self.get_value_from_css(soup, self.selectors.address),
            self.get_value_from_css(soup, self.selectors.descrip),
            self.get_value_from_css(soup, list_since_selector),
            self.get_value_from_css(soup, self.selectors.zip_code),
            self.get_value_from_css(soup, self.selectors.size),
            self.get_value_from_css(soup, self.selectors.year),
            self.get_value_from_css(soup, self.selectors.living_area),
            self.get_value_from_css(soup, self.selectors.kind_of_house),
            self.get_value_from_css(soup, self.selectors.building_type),
            self.get_value_from_css(soup, self.selectors.num_of_rooms),
            self.get_value_from_css(soup, self.selectors.num_of_bathrooms),
            self.get_value_from_css(soup, self.selectors.layout),
            self.get_value_from_css(soup, self.selectors.energy_label),
            self.get_value_from_css(soup, self.selectors.insulation),
            self.get_value_from_css(soup, self.selectors.heating),
            self.get_value_from_css(soup, self.selectors.ownership),
            self.get_value_from_css(soup, self.selectors.exteriors),
            self.get_value_from_css(soup, self.selectors.parking),
            self.get_value_from_css(soup, self.selectors.neighborhood_name),
            self.get_value_from_css(soup, self.selectors.date_list),
            self.get_value_from_css(soup, self.selectors.date_sold),
            self.get_value_from_css(soup, self.selectors.term),
            self.get_value_from_css(soup, self.selectors.price_sold),
            self.get_value_from_css(soup, self.selectors.last_ask_price),
            self.get_value_from_css(soup, self.selectors.last_ask_price_m2).split("\r")[0],
        ]

        # Deal with list_since_selector especially, since its CSS varies sometimes
        if clean_date_format(result[4]) == "na":
            for i in range(6, 16):
                selector = f".fd-align-items-center:nth-child({i}) span"
                update_list_since = self.get_value_from_css(soup, selector)
                if clean_date_format(update_list_since) == "na":
                    pass
                result[4] = update_list_since

        photos = [
            max(
                group.get('data-lazy-srcset').split(', '), 
                key=lambda x: int(x.split()[1][:-1]),
            ).split()[0]
            for group in soup.select(self.selectors.photo)
        ]
        photos_string = ' '.join(photos)

        # Clean up the retried result from one page
        result = [r.replace("\n", "").replace("\r", "").strip() for r in result]
        result.append(photos_string)
        return result

    def scrape_pages(self) -> None:
        """Scrape all the content acoss multiple pages."""

        logger.info("*** Phase 2: Start scraping from individual links ***")
        df = pd.DataFrame({key: [] for key in self.selectors.keys()})

        # Scrape pages with multiprocessing to improve efficiency
        # TODO: use asynctio instead
        pools = mp.cpu_count()
        content = process_map(self.scrape_one_link, self.links, max_workers=pools)

        for c in content:
            df.loc[len(df)] = c

        df["zip_code"] = df["zip_code"].map(find_zip_code)
        df["city"] = df["url"].map(lambda x: x.split("/")[4])
        df["log_id"] = datetime.datetime.now().strftime("%Y%m-%d%H-%M%S")
        if not self.find_past:
            df = df.drop(["term", "price_sold", "date_sold"], axis=1)
        logger.info(f"*** All scraping done: {df.shape[0]} results ***")
        self.raw_df = df

    def save_csv(self, df: pd.DataFrame, filepath: str | None = None) -> None:
        """Save the result to a .csv file."""
        if not filepath:
            tmp_dir = self._create_temporal_directory()
            date = str(datetime.datetime.now().date()).replace("-", "")
            status = "unavailable" if self.find_past else "unavailable"
            filepath = f"{tmp_dir}/houseprice_{date}_{self.area}_{self.want_to.value}_{status}_{len(self.links)}.csv"
        df.to_csv(filepath, index=False)
        logger.info(f"*** File saved: {filepath}. ***")

    def run(
        self, raw_data: bool = False, save: bool = False, filepath: str = None
    ) -> pd.DataFrame:
        """
        Scrape all links and all content.

        :param raw_data: if true, the data won't be pre-processed
        :param save: if true, the data will be saved as a csv file
        :param filepath: the name for the file
        :return: the (pre-processed) dataframe from scraping
        """
        self.fetch_all_links()
        self.scrape_pages()

        if raw_data:
            df = self.raw_df
        else:
            logger.info("*** Cleaning data ***")
            df = preprocess_data(df=self.raw_df, is_past=self.find_past)
            self.clean_df = df

        if save:
            self.save_csv(df, filepath)

        logger.info("*** Done! ***")
        return df