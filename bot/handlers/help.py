from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.formatting import HELP_TEXT


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="MarkdownV2")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Unknown command. Send /help to see available commands."
    )
