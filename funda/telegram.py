from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from os import environ
from pathlib import Path

import typer

from funda.map import take_screenshot
from funda.logging import logger
from funda.main import from_link as cli_from_link

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
        link = " ".join(context.args)
        result = cli_from_link(link) 
        await update.message.reply_markdown(result.to_markdown())
    except Exception as error:
        logger.error(error)
        await update.message.reply_text('Unable to retrieve location, see logs.')


@app.command
def run():
    """Run the telegram bot"""

    app = ApplicationBuilder().token(environ.get('TELEGRAM_TOKEN')).build()
    app.add_handler(CommandHandler("whereis", whereis))
    app.run_polling()


if __name__ == '__name__':
    app()