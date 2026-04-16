import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from db import get_session, repositories
from bot.utils.formatting import format_future_stock, split_message


async def future_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        def _query():
            with get_session() as db:
                return repositories.get_future_stock(db)

        result = await asyncio.to_thread(_query)
        text = format_future_stock(result)
    except Exception:
        await update.message.reply_text(
            "⚠️ Could not reach the inventory database. Please try again in a moment."
        )
        return

    for chunk in split_message(text):
        await update.message.reply_text(chunk, parse_mode="Markdown")
