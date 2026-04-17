# Research: Shared Database Layer

**Branch**: `002-shared-db-layer` | **Date**: 2026-04-16

## Decision 1: Shared Package Location and Name

**Decision**: Create `db/` as a top-level Python package at the project root.

**Rationale**: A top-level `db/` package is importable by both `backend/` and `bot/` with standard `from db.xxx import yyy` syntax, requiring no path manipulation. It is the canonical Python monorepo pattern for shared internal libraries. Alternative names like `shared/` or `core/` are more generic; `db/` is precise and self-documenting for this scope.

**Alternatives considered**:
- `shared/` — Too broad; implies more than database code
- `backend/src/db/` — Would still require path hacks for the bot
- Install as editable package (`pip install -e .`) — Adds packaging overhead not needed for a single-repo project; overkill here

## Decision 2: Internal Package Structure

**Decision**: Four sub-modules within `db/`:

```
db/
├── __init__.py       # Public API: re-exports engine, get_session, get_db, models, repositories
├── engine.py         # Engine + SessionLocal, configured from DATABASE_URL env var
├── models.py         # All SQLAlchemy ORM models and enums (moved from backend/src/models.py)
└── repositories.py   # All query functions (merged from crud.py + bot_crud.py)
```

**Rationale**: Flat structure matching the actual scope — there are only two tables and a small query set. A `repositories/` sub-package with one file per entity is over-engineering for this scale. The flat layout is readable, navigable, and matches what a senior engineer would reach for before the codebase grows to need more structure.

**Alternatives considered**:
- One file per entity in `repositories/` — Premature at 2 models
- Everything in one `db.py` file — Hard to navigate once queries accumulate
- Repository classes (OOP) — Adds abstraction without benefit at this scale; function-based is idiomatic SQLAlchemy

## Decision 3: Session Lifecycle Utilities

**Decision**: Two session utilities exposed from `db/engine.py`:

1. `get_session()` — `contextmanager` for sync callers (bot's `asyncio.to_thread`, tests). Commits on success, rolls back on exception, always closes.
2. `get_db()` — FastAPI `Depends`-compatible generator. Same commit/rollback/close logic. Replaces the current `get_db()` in `backend/src/database.py`.

**Rationale**: These are two different calling conventions for the same lifecycle. Keeping them together in `engine.py` makes it clear they share the same underlying behaviour. The FastAPI dependency pattern is a generator (`yield`); the bot/test pattern uses `contextmanager`. Both are standard Python idioms.

**Alternatives considered**:
- Single utility with mode flag — Overly complex; two small functions are clearer
- Class-based session manager — Adds state where none is needed

## Decision 4: SQLite Concurrency Configuration

**Decision**: Configure the SQLite engine with `check_same_thread=False` and `pool_size` / `pool_pre_ping` disabled (SQLite does not use connection pooling). Use `StaticPool` when running with an in-memory database (for tests).

**Rationale**: The current config already uses `check_same_thread=False`. For SQLite, `NullPool` is the correct pool class for multi-threaded use — it creates a new connection per request rather than pooling, which avoids the "database is locked" error that SQLite produces under concurrent writes. `NullPool` is the SQLAlchemy-recommended approach for SQLite in threaded environments.

**Alternatives considered**:
- `StaticPool` for all environments — Only appropriate for in-memory test databases
- Default connection pool — Causes SQLite locking errors under concurrent bot + server writes

## Decision 5: Environment Variable Configuration

**Decision**: Read `DATABASE_URL` from the environment using `os.environ.get("DATABASE_URL", "sqlite:///./inventory.db")`. Log a `WARNING` if the default is used. If the URL is set but malformed, SQLAlchemy will raise on first connection attempt — catch and re-raise with a clear message.

**Rationale**: Standard 12-factor app pattern. No external config library needed (`python-dotenv` is not in the current requirements and adds a dependency for something a single `os.environ.get` handles).

**Alternatives considered**:
- `pydantic-settings` — Already in `requirements.txt` as `pydantic-settings`; could use it, but overkill for one variable
- `.env` file parsing — Adds `python-dotenv` dependency; not needed for this scope

## Decision 6: Migration of Existing Code

**Decision**:

| Old file | Action |
|----------|--------|
| `backend/src/database.py` | Replace contents with `from db.engine import engine, SessionLocal, get_db` (thin shim for any missed import sites) OR delete if all references are updated |
| `backend/src/models.py` | Replace contents with `from db.models import *` shim OR delete after updating all imports |
| `backend/src/crud.py` | Delete after migrating queries to `db/repositories.py` |
| `backend/src/bot_crud.py` | Delete after migrating queries to `db/repositories.py` |
| `bot/utils/db.py` | Delete; replace usages with `from db.engine import get_session` |

**Decision on shims**: Keep thin shims in `backend/src/database.py` and `backend/src/models.py` for one release to ease the transition, then document them for removal. This avoids a big-bang migration that could miss import sites.

**Rationale**: Incremental is safer. The shims cost 2 lines each and make the diff reviewable. If any import site is missed, it degrades gracefully rather than crashing.

## Decision 7: Query Function Consolidation

**Decision**: Merge `backend/src/crud.py` (4 functions) and `backend/src/bot_crud.py` (6 functions) into `db/repositories.py` (8–9 functions after deduplication). All functions take `db: Session` as first argument — same signature convention already in use.

Functions in `db/repositories.py`:

| Function | Source |
|----------|--------|
| `create_dress(db, dress_data)` | crud.py → `create_dress_inventory` |
| `get_all_dresses(db, skip, limit)` | crud.py → `get_dress_inventory` |
| `get_live_stock(db)` | bot_crud.py |
| `get_future_stock(db)` | bot_crud.py |
| `get_dresses_by_model(db, model_number)` | bot_crud.py |
| `create_order(db, order_data)` | crud.py → `create_active_order` |
| `get_all_orders(db, skip, limit)` | crud.py → `get_active_orders` |
| `get_orders_filtered(db, days)` | bot_crud.py |
| `link_order_to_dress(db, order_id, dress_id)` | crud.py |
| `update_dress_status(db, item_id, new_status)` | bot_crud.py |
| `add_dress(db, ...)` | bot_crud.py |

## All Decisions Resolved

No NEEDS CLARIFICATION items remain.
