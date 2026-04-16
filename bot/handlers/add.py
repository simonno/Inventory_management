import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.db import get_db_session
from bot.utils.formatting import format_dress_added
from backend.src import bot_crud
from backend.src.models import CupSize, StorageLocation

USAGE = (
    'Usage: /add <model> <size> <cup> <location>\n'
    'Example: /add 1234 38 B "tel aviv"\n'
    f'Valid cup sizes: {", ".join(e.value for e in CupSize)}\n'
    f'Valid locations: {", ".join(e.value for e in StorageLocation)}'
)


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or len(context.args) < 4:
        await update.message.reply_text(USAGE)
        return

    model = context.args[0]
    size = context.args[1]
    cup = context.args[2]
    location = " ".join(context.args[3:])

    try:
        def _query():
            with get_db_session() as db:
                return bot_crud.add_dress(db, model, size, cup, location)

        dress = await asyncio.to_thread(_query)
    except ValueError as e:
        await update.message.reply_text(str(e))
        return
    except Exception:
        await update.message.reply_text(
            "⚠️ Could not reach the inventory database. Please try again in a moment."
        )
        return

    await update.message.reply_text(format_dress_added(dress), parse_mode="Markdown")
