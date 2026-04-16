# Implementation Plan: Telegram Inventory Bot

**Branch**: `001-telegram-inventory-bot` | **Date**: 2026-04-16 | **Spec**: [spec.md](./spec.md)

## Summary

Add a Telegram bot that lets boutique staff manage the bridal dress inventory via slash commands. The bot shares the existing SQLite database directly (no HTTP layer between bot and data), adds bot-specific query functions to the backend, and runs as a standalone Python process using `python-telegram-bot` v20+ with long polling.

## Technical Context

**Language/Version**: Python 3.9 (matches existing backend venv)
**Primary Dependencies**: `python-telegram-bot==20.*`, SQLAlchemy (existing), Pydantic (existing)
**Storage**: SQLite (`inventory.db`) — shared with FastAPI backend, no separate DB
**Testing**: pytest (consistent with Python ecosystem; add `bot/tests/` directory)
**Target Platform**: Local machine or simple VPS (Linux); long polling, no public URL required
**Project Type**: Telegram bot service (new module within existing web-app monorepo)
**Performance Goals**: Response in under 3 seconds per command for a team of <10 users
**Constraints**: Must not break existing FastAPI backend; read/write same SQLite file safely
**Scale/Scope**: <10 concurrent users; <50 inventory items; low message volume

## Constitution Check

The project constitution file is a placeholder template (not customized for this project). Applying general good-practice gates:

| Gate | Status | Notes |
|------|--------|-------|
| No new database introduced | ✅ Pass | Reuses `inventory.db` |
| No duplication of existing models | ✅ Pass | Imports from `backend/src/` |
| Complexity justified | ✅ Pass | New module is minimal; no extra abstraction layers |
| Tests required | ✅ Pass | Unit tests for CRUD functions + handler parsing |

## Project Structure

### Documentation (this feature)

```text
specs/001-telegram-inventory-bot/
├── plan.md              # This file
├── research.md          # Phase 0 — library & architecture decisions
├── data-model.md        # Phase 1 — entity reference + new CRUD functions
├── quickstart.md        # Phase 1 — setup and run instructions
├── contracts/
│   └── bot-commands.md  # Phase 1 — full slash command contract
└── tasks.md             # Phase 2 — created by /speckit.tasks (not yet)
```

### Source Code Layout

```text
bot/
├── __init__.py
├── main.py                  # Polling entry point; registers all handlers
├── handlers/
│   ├── __init__.py
│   ├── stock.py             # /stock
│   ├── future.py            # /future
│   ├── dress.py             # /dress <model>
│   ├── orders.py            # /orders [days]
│   ├── status.py            # /status <item_id> <new_status>
│   ├── add.py               # /add <model> <size> <cup> <location>
│   └── help.py              # /help + unknown command fallback
└── utils/
    ├── __init__.py
    ├── formatting.py        # Response formatters; message splitter (4096 char limit)
    └── db.py                # Thread-safe DB session helper for async handlers

backend/src/
└── bot_crud.py              # NEW: bot-specific query functions

bot-requirements.txt         # python-telegram-bot==20.*
bot/tests/
├── test_bot_crud.py         # Unit tests for all bot_crud functions
└── test_handlers.py         # Unit tests for argument parsing in handlers
```

**Structure Decision**: Existing monorepo has `backend/` and `frontend/`. The bot is added as a peer `bot/` module. It imports `backend/src/` directly for models and database access. No changes to `backend/` except adding `bot_crud.py`.

## Implementation Phases

### Phase A: Data Layer (backend/src/bot_crud.py)

Add five query functions reusing existing models and DB session:

1. `get_live_stock(db)` — dresses with status In Stock or Display, ordered by model/size
2. `get_future_stock(db)` — dresses In Sewing/Abroad/Out to Bride + New Order type orders
3. `get_dresses_by_model(db, model_number)` — all dresses for a model with linked orders
4. `get_orders_filtered(db, days=None)` — orders sorted by wedding date, optional date filter
5. `update_dress_status(db, item_id, new_status)` — update status with enum validation
6. `add_dress(db, model_number, size, cup_size, location, condition='Good', notes=None)` — create new dress

### Phase B: Bot Utilities (bot/utils/)

1. `db.py` — `get_db_session()` context manager; wraps sync SQLAlchemy session for use in `asyncio.to_thread()`
2. `formatting.py` — one formatter per command response; `split_message(text, limit=4096)` for long responses

### Phase C: Command Handlers (bot/handlers/)

One handler module per slash command. Each handler:
- Parses and validates arguments
- Calls the appropriate `bot_crud` function via `asyncio.to_thread()`
- Formats the result using `formatting.py`
- Sends response (split if needed)
- Returns a clear error message on bad input or DB failure

Handler modules: `stock.py`, `future.py`, `dress.py`, `orders.py`, `status.py`, `add.py`, `help.py`

### Phase D: Bot Entry Point (bot/main.py)

- Loads `TELEGRAM_BOT_TOKEN` from environment variable
- Registers all `CommandHandler` instances
- Registers `MessageHandler` fallback for unknown text (→ `/help`)
- Starts polling loop

### Phase E: Tests (bot/tests/)

- `test_bot_crud.py`: test each CRUD function against a temporary in-memory SQLite DB
- `test_handlers.py`: test argument parsing logic (no Telegram API calls)

## Complexity Tracking

No constitution violations. No extra complexity introduced.

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| python-telegram-bot | 20.* | Telegram Bot API client + command handlers |
| SQLAlchemy | existing | Database ORM (reused from backend) |
| pytest | existing/add | Test runner |

No new infrastructure required. Bot shares `inventory.db` with the backend.
