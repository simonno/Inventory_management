import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from db import get_session, repositories
from bot.utils.formatting import format_live_stock, split_message


async def stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        def _query():
            with get_session() as db:
                return repositories.get_live_stock(db)

        dresses = await asyncio.to_thread(_query)
        text = format_live_stock(dresses)
    except Exception:
        await update.message.reply_text(
            "⚠️ Could not reach the inventory database. Please try again in a moment."
        )
        return

    for chunk in split_message(text):
        await update.message.reply_text(chunk, parse_mode="Markdown")
