import typer

from funda.types import HousingType
from funda.utils import positive_integer
from funda.scraper import FundaScraper

app = typer.Typer()

@app.command()
def main(
    city: str = typer.Option("eindhoven", help="Specify which area you are looking for"),
    want_to: HousingType = typer.Option(HousingType.buy, help="Specify you want"),
    find_past: bool = typer.Option(False, help="Indicate whether you want to use historical data or not"),
    page_start: int = typer.Option(1, help="Specify which page to start scraping"),
    n_pages: int = typer.Option(1, help="Specify how many pages to scrape"),
    min_price: int = typer.Option(None, help="Specify the min price", callback=positive_integer),
    max_price: int = typer.Option(None, help="Specify the max price", callback=positive_integer),
    days_since: int = typer.Option(None, help="Specify the days since publication (1, 3, 5, 10, 30)"),
    raw_data: bool = typer.Option(False, help="Indicate whether you want the raw scraping result or preprocessed one"),
    save: bool = typer.Option(True, help="Indicate whether you want to save the data or not"),
):
    funda_scraper = FundaScraper(
        area=city,
        want_to=want_to,
        find_past=find_past,
        page_start=page_start,
        n_pages=n_pages,
        min_price=min_price,
        max_price=max_price,
        days_since=days_since,
    )
    df = funda_scraper.run(raw_data=raw_data, save=save)
    print(df.head())

if __name__ == '__main__':
    app()
