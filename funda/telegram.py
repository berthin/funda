from telegram import Update, InputMediaPhoto
from telegram.error import RetryAfter
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from os import environ
from pathlib import Path

import typer

from funda.map import take_screenshot
from funda.logging import logger
from funda.main import from_link as cli_from_link

from funda.report import to_markdown
from funda.report import find_photos
from tempfile import TemporaryDirectory

from time import sleep

app = typer.Typer()


async def whereis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        address = " ".join(context.args)
        screenshot_path = Path(f'data/{address}.png')
        take_screenshot(address, screenshot_path)
        await update.message.reply_photo(screenshot_path)
    except Exception as error:
        logger.error(error)
        await update.message.reply_text('Unable to retrieve location, see logs.')


async def from_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info('Formatting message')
        link = " ".join(context.args)
        listing_md = Path('tmp.md')
        listing = cli_from_link(link)
        md = to_markdown(listing)
        md.save(listing_md)

        logger.info('Sending listing information')
        await update.message.reply_markdown(md.contents())

        with TemporaryDirectory() as tmp_dir:
            logger.info('Generating description')
            tmp_file = Path(tmp_dir) / listing.address

            tmp_file.write_text(listing.to_string())
            logger.info('Sending description for listing as document')
            await update.message.reply_document(str(tmp_file))

        logger.info('Generating media group')
        logger.info(find_photos(listing))

        photos = find_photos(listing)
        number_of_photos = len(photos)
        max_photos_per_group = 5
        nth = (number_of_photos + max_photos_per_group - 1) // max_photos_per_group
        for ith, group in enumerate(range(0, number_of_photos, max_photos_per_group), start=1):
            media_group = [
                InputMediaPhoto(open(str(photo), 'rb'))
                for photo in photos[group: min(group + max_photos_per_group, number_of_photos)]
            ]
            logger.info(f'Sending photos (group {ith} out of {nth})')
            sleep(4) # sleep 4 seconds to avoid telegram flood control exceeded error

            sent = False
            for reply_attempt in range(5):
                try:
                    await update.message.reply_media_group(media_group, write_timeout=120, connect_timeout=120, pool_timeout=120, read_timeout=120)
                    send = True
                    break
                except RetryAfter as flood_error:
                    logger.warning(f'Got FloodError... waiting {flood_error.retry_after}')
                    sleep(flood_error.retry_after)
            if not sent:
                logger.error('Was not able to sent the photos.')
            

    except Exception as error:
        logger.error(error)
        await update.message.reply_text('Something went wrong, see logs.')


@app.command()
def run():
    """Run the telegram bot"""

    app = ApplicationBuilder().token(environ.get('TELEGRAM_TOKEN')).build()
    app.add_handler(CommandHandler("whereis", whereis))
    app.add_handler(CommandHandler("from", from_link))
    app.run_polling()


if __name__ == '__main__':
    app()