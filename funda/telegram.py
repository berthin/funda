from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from os import environ
from pathlib import Path

from funda.map import take_screenshot
from funda.logging import logger


async def whereis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #chat_id = update.effective_message.chat_id
    try:
        address = " ".join(context.args)
        screenshot_path = Path(f'data/{address}.png')
        take_screenshot(address, screenshot_path)
        await update.message.reply_photo(screenshot_path)
    except Exception as error:
        logger.error(error)
        await update.message.reply_text('Unable to retrieve location, see logs.')
    #await update.message.reply_text(f'Hello {update.effective_user.first_name}')


app = ApplicationBuilder().token(environ.get('TELEGRAM_TOKEN')).build()

app.add_handler(CommandHandler("whereis", whereis))

app.run_polling()