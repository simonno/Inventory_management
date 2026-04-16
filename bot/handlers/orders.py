import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from db import get_session, repositories
from bot.utils.formatting import format_orders, split_message

USAGE = "Usage: /orders or /orders <days>\nExample: /orders 30"


async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    days = None
    if context.args:
        try:
            days = int(context.args[0])
            if days <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text(f"Days must be a positive number.\n{USAGE}")
            return

    try:
        def _query():
            with get_session() as db:
                return repositories.get_orders_filtered(db, days=days)

        orders = await asyncio.to_thread(_query)
    except Exception:
        await update.message.reply_text(
            "⚠️ Could not reach the inventory database. Please try again in a moment."
        )
        return

    text = format_orders(orders, days=days)
    for chunk in split_message(text):
        await update.message.reply_text(chunk, parse_mode="Markdown")
