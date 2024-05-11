from funda.markdown import MarkdownDocument

import pandas as pd
from pandas.core.series import Series
from tqdm.contrib.concurrent import process_map
import multiprocessing as mp
from pathlib import Path

from funda.logging import logger

from curl_cffi import requests
from funda.utils import decode_photo_stream
from typing import Any


def to_markdown(listing: Series) -> None:
    md = MarkdownDocument()

    basic_info_fields = ["url", "address", "zip_code", "neighborhood_name"]
    property_details_fields = ["size", "living_area", "year", "kind_of_house", "building_type", "num_of_rooms", "num_of_bathrooms", "energy_label", "insulation", "heating", "ownership"]
    listing_details_fields = ["price", "listed_since", "date_list", "last_ask_price", "last_ask_price_m2"]
    additional_info_fields = [
        # "descrip",
        "layout", "exteriors", "parking", "date_sold", "term", "price_sold", 
        #"photo",
    ]

    # Basic Information
    md.add_bold('Basic Information', breakline=True)
    for field in basic_info_fields:
        md.add_bold(f'{field.capitalize()}: ').add_normal(listing[field], breakline=True)

    # Property Details
    md.add_normal('\n').add_bold('Property Details', breakline=True)
    for field in property_details_fields:
        md.add_bold(f'{field.capitalize()}: ').add_normal(listing[field], breakline=True)

    # Listing Details
    md.add_normal('\n').add_bold('Listing Details', breakline=True)
    for field in listing_details_fields:
        md.add_bold(f'{field.capitalize()}: ').add_normal(listing[field], breakline=True)

    # Additional Information
    md.add_normal('\n').add_bold('Additional Information', breakline=True)
    for field in additional_info_fields:
        md.add_bold(f'{field.capitalize()}: ').add_normal(listing[field], breakline=True)

    return md


def download_photo(photo_info: dict[str, Any], save_to_directory: Path) -> Path:
    response = requests.get(photo_info['url'])
    if not response.ok:
        logger.error(f'Failed download: {photo_info}')
        return
        
    filepath = save_to_directory / f'{photo_info["name"]}.{photo_info["extension"]}'
    filepath.write_bytes(response.content)
    return filepath
    

def _download_photo(args) -> Path:
    return download_photo(args[0], args[1])

def find_photos(listing: Series, force: bool = False) -> list[Path]:
    directory = Path(f'data/{listing.address}/photos')
    if directory.exists() and not force:
        logger.info(f'Found {directory}. Will reuse its contents')
        return list(directory.glob('*'))
    
    directory.mkdir(parents=True, exist_ok=True)

    pools = mp.cpu_count()
    photos = decode_photo_stream(listing.photos)
    return process_map(
        _download_photo,
        zip(photos, [directory] * len(photos)),
        max_workers=pools,
    )