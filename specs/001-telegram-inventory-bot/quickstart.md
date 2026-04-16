# Quickstart: Telegram Inventory Bot

**Branch**: `001-telegram-inventory-bot` | **Date**: 2026-04-16

## Prerequisites

- Python 3.9+ (same as backend)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- The existing `inventory.db` SQLite database (created by the backend)

## Project Structure

```text
bot/
├── __init__.py
├── main.py              # Entry point — starts polling
├── handlers/
│   ├── __init__.py
│   ├── stock.py         # /stock handler
│   ├── future.py        # /future handler
│   ├── dress.py         # /dress handler
│   ├── orders.py        # /orders handler
│   ├── status.py        # /status handler
│   ├── add.py           # /add handler
│   └── help.py          # /help + fallback handler
└── utils/
    ├── __init__.py
    ├── formatting.py    # Message formatting & splitting helpers
    └── db.py            # DB session helper for async context

backend/src/
├── bot_crud.py          # NEW: bot-specific query functions (added in this feature)
├── crud.py              # Existing — unchanged
├── models.py            # Existing — unchanged
├── database.py          # Existing — unchanged
└── schemas.py           # Existing — unchanged

bot-requirements.txt     # Bot-specific Python dependencies
```

## Setup

1. **Install bot dependencies**:
   ```bash
   pip install python-telegram-bot==20.* 
   # Or: pip install -r bot-requirements.txt
   ```

2. **Set environment variable**:
   ```bash
   export TELEGRAM_BOT_TOKEN="your-bot-token-here"
   ```

3. **Register commands with BotFather**:
   - Open [@BotFather](https://t.me/BotFather) in Telegram
   - Send `/setcommands` and paste the command list from `contracts/bot-commands.md`

4. **Run the bot**:
   ```bash
   python -m bot.main
   ```

   The bot will start polling. It shares the same `inventory.db` as the backend — ensure the backend has initialized the database first (`python -m uvicorn backend.src.main:app` once, or run the backend normally).

## Dependencies (`bot-requirements.txt`)

```
python-telegram-bot==20.*
```

No additional dependencies — the bot reuses the existing SQLAlchemy/Pydantic stack from the backend.

## Key Design Notes

- **Shared database**: The bot reads and writes `inventory.db` directly via SQLAlchemy, the same file used by the FastAPI backend. No HTTP calls between bot and backend.
- **Thread safety**: SQLAlchemy sessions are created per-request inside `asyncio.to_thread()` to avoid blocking the bot's async event loop.
- **Message splitting**: Any response exceeding 4096 characters is automatically split at newline boundaries into multiple sequential messages.
- **No auth**: All users in the configured Telegram chat can use all commands. Access is controlled at the Telegram level (private group membership).

## Running in Production

For a simple VPS deployment, run with a process manager:
```bash
# Using systemd or screen/tmux:
python -m bot.main &
```

Webhook deployment (optional, for future): requires a public HTTPS URL and SSL certificate.
