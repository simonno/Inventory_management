import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.db import get_db_session
from bot.utils.formatting import format_dress_detail, split_message
from backend.src import bot_crud

USAGE = "Usage: /dress <model_number>\nExample: /dress 1234"


async def dress_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(USAGE)
        return

    model_number = " ".join(context.args)

    try:
        def _query():
            with get_db_session() as db:
                return bot_crud.get_dresses_by_model(db, model_number)

        dresses = await asyncio.to_thread(_query)
    except Exception:
        await update.message.reply_text(
            "⚠️ Could not reach the inventory database. Please try again in a moment."
        )
        return

    text = format_dress_detail(dresses)
    if text is None:
        await update.message.reply_text(
            f"No dresses found with model number '{model_number}'."
        )
        return

    for chunk in split_message(text):
        await update.message.reply_text(chunk, parse_mode="Markdown")
