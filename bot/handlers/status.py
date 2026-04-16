import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.db import get_db_session
from bot.utils.formatting import format_status_update, split_message, VALID_STATUSES_TEXT
from backend.src import bot_crud
from backend.src.models import DressStatus

USAGE = "Usage: /status <item_id> <new_status>\nExample: /status 7 in sewing"


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(USAGE)
        return

    try:
        item_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(f"item_id must be a number.\n{USAGE}")
        return

    new_status_raw = " ".join(context.args[1:])
    new_status_normalized = new_status_raw.title()

    try:
        def _query():
            with get_db_session() as db:
                old = db.query(bot_crud.models.DressInventory).filter(
                    bot_crud.models.DressInventory.item_id == item_id
                ).first()
                old_status = old.status.value if old else None
                updated = bot_crud.update_dress_status(db, item_id, new_status_normalized)
                return old_status, updated

        old_status, dress = await asyncio.to_thread(_query)
    except ValueError:
        await update.message.reply_text(
            f"Invalid status '{new_status_raw}'. Valid options:\n{VALID_STATUSES_TEXT}"
        )
        return
    except Exception:
        await update.message.reply_text(
            "⚠️ Could not reach the inventory database. Please try again in a moment."
        )
        return

    if dress is None:
        await update.message.reply_text(
            f"Dress #{item_id} not found. Use /dress <model> to look up item IDs."
        )
        return

    text = format_status_update(old_status, dress)
    await update.message.reply_text(text, parse_mode="Markdown")
