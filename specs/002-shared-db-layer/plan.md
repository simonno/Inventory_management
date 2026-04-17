# Implementation Plan: Shared Database Layer

**Branch**: `002-shared-db-layer` | **Date**: 2026-04-16 | **Spec**: [spec.md](./spec.md)

## Summary

Consolidate the project's scattered database concerns — engine config in `backend/src/database.py`, models in `backend/src/models.py`, server queries in `backend/src/crud.py`, and bot queries in `backend/src/bot_crud.py` — into a single top-level `db/` Python package. The package provides a clean public API (engine, session utilities, models, all query functions) importable by both consumers without any path manipulation. `bot/utils/db.py` (which currently uses `sys.path.insert`) is deleted and replaced with a direct import.

## Technical Context

**Language/Version**: Python 3.9 (existing venv)
**Primary Dependencies**: SQLAlchemy (existing), Pydantic (existing) — no new dependencies required
**Storage**: SQLite (`inventory.db`) — unchanged; `NullPool` added for thread safety
**Testing**: pytest with in-memory SQLite override via `DATABASE_URL` env var
**Target Platform**: Local machine / VPS — same as existing deployment
**Project Type**: Internal shared library within an existing monorepo (FastAPI server + Telegram bot)
**Performance Goals**: No regression from current; `NullPool` is equivalent or better for SQLite under concurrent load
**Constraints**: Zero functional regression — all API endpoints and bot commands must behave identically after migration
**Scale/Scope**: 2 ORM models, 11 query functions, 2 consumers

## Constitution Check

Constitution file is a placeholder template — no custom gates. Standard good-practice gates:

| Gate | Status | Notes |
|------|--------|-------|
| No new database introduced | ✅ Pass | Same SQLite file, same schema |
| No duplication of models | ✅ Pass | `backend/src/models.py` becomes a shim then removed |
| Complexity justified | ✅ Pass | Reduces complexity; fewer files, clearer structure |
| No breaking API changes | ✅ Pass | All endpoints and bot commands preserved via shims during transition |
| Tests must pass after migration | ✅ Pass | Existing tests updated to import from `db` |

## Project Structure

### Documentation (this feature)

```text
specs/002-shared-db-layer/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── db-package-api.md
└── tasks.md             # Created by /speckit.tasks
```

### Source Code Changes

```text
# NEW
db/
├── __init__.py          # Public API re-exports
├── engine.py            # Engine + NullPool + get_session() + get_db()
├── models.py            # All ORM models and enums
└── repositories.py      # All query functions (merged)

# MODIFIED
backend/src/main.py      # Update imports to db.*
backend/src/schemas.py   # Update model imports to db.models
bot/handlers/*.py        # Replace bot_crud + get_db_session with db.*
bot/tests/test_bot_crud.py  # Update imports

# REPLACED WITH SHIMS
backend/src/database.py  # from db.engine import ...
backend/src/models.py    # from db.models import *
backend/src/crud.py      # from db.repositories import *

# DELETED
backend/src/bot_crud.py
bot/utils/db.py
```

## Implementation Phases

### Phase A: Create `db/` Package

Build the new package — no existing files touched yet.

1. `db/__init__.py` — minimal, filled in Phase D
2. `db/engine.py` — `DATABASE_URL` from env with fallback + warning, `NullPool`, `SessionLocal`, `get_session()`, `get_db()`
3. `db/models.py` — verbatim copy from `backend/src/models.py`
4. `db/repositories.py` — merge all functions from `crud.py` + `bot_crud.py` with consistent naming and type hints

### Phase B: Replace Backend Internals

1. `backend/src/database.py` → shim
2. `backend/src/models.py` → shim
3. `backend/src/crud.py` → shim
4. `backend/src/main.py` — update to direct `db.*` imports
5. `backend/src/schemas.py` — update model imports
6. Delete `backend/src/bot_crud.py`

### Phase C: Update Bot Consumers

1. Delete `bot/utils/db.py`
2. Update all `bot/handlers/*.py` — `db.repositories` + `db.engine.get_session`
3. Update `bot/tests/test_bot_crud.py` — `DATABASE_URL` env override, import from `db`

### Phase D: Wire `db/__init__.py`

Add all public re-exports per `contracts/db-package-api.md`.

### Phase E: Verification

Run full checklist from `quickstart.md` — import smoke tests, both consumers start, all tests pass, grep checks.

## Complexity Tracking

No violations. This feature reduces complexity.
