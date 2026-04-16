# Research: Telegram Inventory Bot

**Branch**: `001-telegram-inventory-bot` | **Date**: 2026-04-16

## Decision 1: Telegram Bot Library

**Decision**: `python-telegram-bot` v20+ (async)

**Rationale**: Best-maintained Python Telegram library with native async support, built-in `CommandHandler` for slash commands, and extensive community adoption. v20+ is fully async (asyncio-based), which pairs well with async SQLAlchemy patterns if needed later.

**Alternatives considered**:
- `aiogram` — excellent async library but steeper learning curve; better suited for high-traffic bots
- `telebot` (pyTelegramBotAPI) — simpler but synchronous-first; less idiomatic with async frameworks
- Telegram Bot API directly (HTTP) — no abstraction; unnecessary complexity

## Decision 2: Bot Architecture

**Decision**: Standalone `bot/` module sharing the existing SQLite database and SQLAlchemy models from `backend/src/`

**Rationale**: The backend already has all models, enums, and a working SQLite connection. The bot can import `backend/src/models.py`, `backend/src/database.py`, and `backend/src/crud.py` directly, avoiding duplication. The bot runs as a separate process (polling or webhook) but reads/writes the same `inventory.db` file.

**Alternatives considered**:
- Bot calls the FastAPI HTTP endpoints — adds network overhead and requires the backend to be running; unnecessary for same-machine deployment
- Bot maintains its own database — violates the shared-data-store assumption from the spec
- Monorepo package — over-engineered for a small boutique tool

## Decision 3: Bot Execution Model

**Decision**: Long polling (not webhook)

**Rationale**: Long polling requires no public URL or SSL certificate, making it trivial to run locally or on a simple VPS. For a small boutique team with low message volume, polling overhead is negligible.

**Alternatives considered**:
- Webhook — requires HTTPS endpoint; better for high-volume production bots; can be added later

## Decision 4: SQLite Threading with Async Bot

**Decision**: Use synchronous SQLAlchemy sessions inside `run_in_executor` calls, or use `asyncio.to_thread` for DB operations

**Rationale**: The existing `database.py` uses synchronous SQLAlchemy with `check_same_thread=False`. The bot will call DB functions in a thread pool to avoid blocking the async event loop. This avoids refactoring the existing database layer.

**Alternatives considered**:
- Migrate to `aiosqlite` / async SQLAlchemy — significant refactor of existing backend; out of scope
- Run bot synchronously — blocks during DB calls; acceptable at low volume but not recommended

## Decision 5: Message Length Splitting

**Decision**: Split responses at 4096 characters (Telegram's limit), breaking on newline boundaries

**Rationale**: `/stock` with many dresses could exceed the limit. Splitting at natural newline boundaries keeps messages readable. `python-telegram-bot` does not do this automatically.

## Decision 6: New CRUD Functions Needed

The following functions must be added to `backend/src/crud.py` (or a new `bot_crud.py`):

| Function | Purpose |
|----------|---------|
| `get_live_stock(db)` | Query dresses with status IN_STOCK or DISPLAY |
| `get_future_stock(db)` | Query dresses with status IN_SEWING, ABROAD, OUT_TO_BRIDE + orders with type NEW_ORDER |
| `get_dresses_by_model(db, model_number)` | All dresses matching a model_number with linked orders |
| `get_orders_filtered(db, days=None)` | All orders, optionally filtered by wedding_date within N days |
| `update_dress_status(db, item_id, new_status)` | Update dress status by item_id |

**Decision**: Add to a new `backend/src/bot_crud.py` to keep bot-specific queries separate from core CRUD.

## All NEEDS CLARIFICATION: Resolved

No unknowns remain. All decisions above resolve the technical gaps.
