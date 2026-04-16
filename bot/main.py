"""Telegram bot entry point for the Bridal Inventory Management System."""

import os
import sys
import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.handlers.help import help_command, unknown_command
from bot.handlers.stock import stock_command
from bot.handlers.future import future_command
from bot.handlers.dress import dress_command
from bot.handlers.orders import orders_command
from bot.handlers.status import status_command
from bot.handlers.add import add_command

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print(
            "Error: TELEGRAM_BOT_TOKEN environment variable is not set.\n"
            "Set it with: export TELEGRAM_BOT_TOKEN='your-bot-token'\n"
            "Get a token from @BotFather on Telegram."
        )
        sys.exit(1)

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stock", stock_command))
    app.add_handler(CommandHandler("future", future_command))
    app.add_handler(CommandHandler("dress", dress_command))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_command))

    logger.info("Bot started. Polling for updates...")
    app.run_polling()


if __name__ == "__main__":
    main()
