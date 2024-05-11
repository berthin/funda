import typer
import re
from funda.logging import logger

ZIP_CODE_PATTERN = re.compile('\d{4}\s+\w{2}')


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