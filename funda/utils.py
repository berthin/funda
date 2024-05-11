import typer
import re
from funda.logging import logger
from typing import Iterable, Any

ZIP_CODE_PATTERN = re.compile('\d{4}\s+\w{2}')
FUNDA_CLOUD_SERVER = 'https://cloud.funda.nl/'
PHOTO_RESOLUTION_SEPARATOR = '$$'
#https://cloud.funda.nl/valentina_media/190/205/179_2160x1440.jpg
PHOTO_ENCODED_URL_PATTERN = re.compile(f'^{FUNDA_CLOUD_SERVER}(?P<name>.*)_(?P<dimensions>\d+x\d+)\.(?P<extension>.+)$')


def positive_integer(value: str | None) -> int | None:
    if value is None:
        return value
    try:
        ivalue = int(value)
        if ivalue < 0:
            raise ValueError()
        return ivalue
    except ValueError:
        raise typer.BadParameter("Must be a positive integer")


def find_zip_code(text: str) -> str:
    match = ZIP_CODE_PATTERN.search(text)

    if match:
        return match.group(0)

    logger.error('Could not parse zip code: {text}')
    return text


def filter_high_resolution_only(photos: dict[str, Any]) -> dict[str, Any]:
    high_resolution_photos = dict()

    for photo in photos:
        photo_name = photo['name']
        if photo_name not in high_resolution_photos:
            high_resolution_photos[photo_name] = photo
            continue
        
        current_resolution = high_resolution_photos[photo_name]['resolution']
        if current_resolution < photo['resolution']:
            high_resolution_photos[photo_name] = photo

    return high_resolution_photos.items()


def encode_photo_stream(text: str) -> list[str]:
    content = text.split()
    urls = content[::2]
    resolutions = content[1::2]
    # assume that resolution ends with "w" (e.g. 1440w)
    return [f'{url}{PHOTO_RESOLUTION_SEPARATOR}{resolution}' for url, resolution in zip(urls, resolutions)]


def decode_photo_stream(text: str) -> list[dict[str, Any]]:
    def photo_to_dict(url: str) -> dict[str, Any]:
        match = PHOTO_ENCODED_URL_PATTERN.match(url)
        if not match:
            logger.error(f'Could not decode the url: {url}')
            return {}

        return {
            'url': url.split(PHOTO_RESOLUTION_SEPARATOR)[0],
            'name': match.group('name').replace('/', '_'),
            'extension': match.group('extension'),
            'dimensions': match.group('dimensions')
        }

    return [
        photo_to_dict(encoded_url)
        for encoded_url in text.split()
    ]