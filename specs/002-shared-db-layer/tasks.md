# Tasks: Shared Database Layer

**Input**: Design documents from `/specs/002-shared-db-layer/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/db-package-api.md ✅ quickstart.md ✅

**Tests**: Not explicitly requested — existing tests updated as part of migration tasks.

**Organization**: Tasks follow Plan Phases A–E. Each phase is independently verifiable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- All paths relative to repository root

---

## Phase 1: Setup

**Purpose**: Create the `db/` package skeleton. Nothing is imported from it yet — no risk of breakage.

- [ ] T001 Create `db/` directory with empty `db/__init__.py`
- [ ] T002 [P] Create `db/engine.py` — read `DATABASE_URL` from `os.environ` with default `sqlite:///./inventory.db`, log `WARNING` if default used; create engine with `NullPool` and `connect_args={"check_same_thread": False}`; create `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`; implement `get_session()` as a `@contextmanager` that yields a session and commits on success / rolls back on exception / always closes; implement `get_db()` as a generator with identical lifecycle for FastAPI `Depends`
- [ ] T003 [P] Create `db/models.py` — copy verbatim from `backend/src/models.py`: all enums (`CupSize`, `OrderType`, `StorageLocation`, `DressCondition`, `DressStatus`) and both ORM models (`DressInventory`, `ActiveOrder`) with their relationship. `Base` must be declared here and imported from `db.engine` (or declared in `db/models.py` and imported into `db/engine.py` — whichever avoids circular imports; declare `Base` in `db/models.py`, import into `db/engine.py`)
- [ ] T004 Create `db/repositories.py` — implement all 11 query functions by merging `backend/src/crud.py` and `backend/src/bot_crud.py`; use consistent naming (see data-model.md migration map); add full type hints; keep `db: Session` as first argument on all functions; `update_dress_status` and `add_dress` raise `ValueError` on invalid enum input; all other functions return `None` for not-found (no HTTP exceptions)
- [ ] T005 Populate `db/__init__.py` — re-export the full public API per `contracts/db-package-api.md`: `engine`, `SessionLocal`, `get_session`, `get_db`, `Base`, `DressInventory`, `ActiveOrder`, all five enums, and `repositories` module

**Checkpoint**: `python -c "from db import get_session, repositories, DressInventory, DressStatus"` succeeds from project root with no errors.

---

## Phase 2: Foundational — Verify Package Before Touching Consumers

**Purpose**: Confirm the new `db/` package is correct in isolation before any existing code is modified. This phase is purely additive — no deletions, no consumer changes.

- [ ] T006 [US1] Run import smoke test: `backend/venv/bin/python -c "from db import get_session, get_db, repositories, DressInventory, ActiveOrder, DressStatus, CupSize, StorageLocation, DressCondition, OrderType, Base"` — fix any import errors before proceeding
- [ ] T007 [US1] Run a quick DB round-trip test: create a temporary script `scripts/verify_db.py` that sets `DATABASE_URL=sqlite:///:memory:`, calls `Base.metadata.create_all(bind=engine)`, opens a `get_session()`, creates one `DressInventory` record, and asserts it can be read back — delete script after passing

**Checkpoint**: Both T006 and T007 pass. `db/` package is confirmed correct. Consumers can now be migrated.

---

## Phase 3: User Story 1 + 2 — Single Source of Truth & Safe Sessions (Priority: P1)

**Goal**: Replace `backend/src/database.py` and `backend/src/models.py` with shims pointing to `db/`. The API server now consumes the shared package exclusively for engine + models.

**Independent Test**: Start the FastAPI server (`uvicorn backend.src.main:app`) — it must start without errors and all endpoints must return correct results.

- [ ] T008 [US1] Replace `backend/src/database.py` with a 3-line shim: `from db.engine import engine, SessionLocal, get_db` and `__all__ = ["engine", "SessionLocal", "get_db"]` — add comment `# TRANSITIONAL SHIM: remove after all imports updated`
- [ ] T009 [US1] Replace `backend/src/models.py` with a shim: `from db.models import *` — add comment `# TRANSITIONAL SHIM: remove after all imports updated`
- [ ] T010 [US1] Update `backend/src/schemas.py` — change `from .models import CupSize, OrderType, StorageLocation, DressCondition, DressStatus` to `from db.models import CupSize, OrderType, StorageLocation, DressCondition, DressStatus`
- [ ] T011 [US1] Update `backend/src/main.py` — replace `from . import crud, models, schemas, database` and `from .database import engine, get_db` with direct imports from `db.*`; ensure `Base.metadata.create_all(bind=engine)` still runs on startup using `from db import Base, engine`
- [ ] T012 [US1] Start the FastAPI server and confirm all four existing endpoints (`GET /inventory/`, `POST /inventory/`, `GET /orders/`, `POST /orders/`, `PUT /orders/{id}/link/{id}`) respond correctly — fix any import errors

**Checkpoint**: FastAPI server starts and serves all endpoints correctly using the shared `db/` package.

---

## Phase 4: User Story 3 — Consolidated Query Layer (Priority: P2)

**Goal**: Replace `backend/src/crud.py` with a shim and delete `backend/src/bot_crud.py`. The server now calls `db/repositories.py` directly; the bot's handlers are updated to call `db/repositories.py`.

**Independent Test**: All bot commands (`/stock`, `/future`, `/dress`, `/orders`, `/status`, `/add`) produce the same output as before. All API endpoints still work. `backend/src/bot_crud.py` no longer exists.

- [ ] T013 [US3] Replace `backend/src/crud.py` with a shim: `from db.repositories import *` — add transitional comment
- [ ] T014 [US3] Delete `backend/src/bot_crud.py` (it is now fully replaced by `db/repositories.py`)
- [ ] T015 [US3] Update `bot/handlers/stock.py` — replace `from backend.src import bot_crud` with `from db import repositories`; replace `bot_crud.get_live_stock(db)` with `repositories.get_live_stock(db)`
- [ ] T016 [US3] [P] Update `bot/handlers/future.py` — same pattern: `from db import repositories`; `repositories.get_future_stock(db)`
- [ ] T017 [US3] [P] Update `bot/handlers/dress.py` — `from db import repositories`; `repositories.get_dresses_by_model(db, model_number)`
- [ ] T018 [US3] [P] Update `bot/handlers/orders.py` — `from db import repositories`; `repositories.get_orders_filtered(db, days=days)`
- [ ] T019 [US3] [P] Update `bot/handlers/status.py` — `from db import repositories`; `repositories.update_dress_status(db, item_id, new_status_normalized)`; also fix the inline model import: replace `bot_crud.models.DressInventory` with `from db import DressInventory`
- [ ] T020 [US3] [P] Update `bot/handlers/add.py` — `from db import repositories`; `repositories.add_dress(db, model, size, cup, location)`; update `CupSize` and `StorageLocation` imports to `from db import CupSize, StorageLocation`

**Checkpoint**: `grep -r "bot_crud" . --include="*.py"` returns zero results. All handlers updated.

---

## Phase 5: User Story 4 — No Path Manipulation (Priority: P2)

**Goal**: Delete `bot/utils/db.py` (which contains the `sys.path.insert` hack) and replace all usages with `from db import get_session`.

**Independent Test**: `grep -r "sys.path" . --include="*.py"` returns zero results. Bot handlers start and connect to the database without any path manipulation.

- [ ] T021 [US4] Update all `bot/handlers/*.py` that import `from bot.utils.db import get_db_session` — replace with `from db import get_session`; replace `get_db_session()` usage with `get_session()` (same context manager protocol, same call sites — only the import changes)
- [ ] T022 [US4] Delete `bot/utils/db.py` — it is now entirely superseded by `db.engine.get_session`
- [ ] T023 [US4] Confirm `bot/utils/__init__.py` still exists and is not broken by the deletion
- [ ] T024 [US4] Run `grep -r "sys.path" . --include="*.py"` and confirm zero results — fix any remaining occurrences

**Checkpoint**: No `sys.path` in the codebase. Bot handlers import cleanly from `db`.

---

## Phase 6: User Story 5 — Environment-Based Configuration (Priority: P3)

**Goal**: Confirm the `DATABASE_URL` env var mechanism works end-to-end for both test isolation and deployment flexibility.

**Independent Test**: Set `DATABASE_URL=sqlite:///:memory:` and run the full test suite — all tests pass against an in-memory DB with no file created on disk.

- [ ] T025 [US5] Update `bot/tests/test_bot_crud.py` — remove the inline `create_engine("sqlite:///:memory:")` fixture; instead set `os.environ["DATABASE_URL"] = "sqlite:///:memory:"` before importing from `db`; use `from db import engine, Base, get_session, repositories`; ensure `Base.metadata.create_all(bind=engine)` is called in the fixture
- [ ] T026 [US5] Run `DATABASE_URL=sqlite:///:memory: backend/venv/bin/python -m pytest bot/tests/ -v` — confirm all 13 tests pass; fix any failures

**Checkpoint**: All 13 tests pass with `DATABASE_URL=sqlite:///:memory:`. No `inventory.db` file created during test run.

---

## Phase 7: Polish & Verification

**Purpose**: Full regression check, grep audits, and final cleanup.

- [ ] T027 [P] Run full verification checklist from `quickstart.md`: import smoke test, both consumers start, all tests pass
- [ ] T028 [P] Run `grep -r "sqlite:///" . --include="*.py"` — confirm only `db/engine.py` contains this string
- [ ] T029 [P] Run `grep -r "sys.path" . --include="*.py"` — confirm zero results
- [ ] T030 [P] Run `grep -r "bot_crud" . --include="*.py"` — confirm zero results
- [ ] T031 Verify FastAPI server starts and all endpoints respond: `GET /`, `GET /inventory/`, `POST /inventory/`, `GET /orders/`, `POST /orders/`, `PUT /orders/{order_id}/link/{dress_id}`
- [ ] T032 Review `backend/src/database.py`, `backend/src/models.py`, `backend/src/crud.py` shims — confirm they are minimal (2–3 lines each) and carry the `# TRANSITIONAL SHIM` comment for future removal

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately; T002, T003 are parallel (different files)
- **Phase 2 (Foundational)**: Depends on Phase 1 completion — must pass before any consumer is touched
- **Phase 3 (US1+2)**: Depends on Phase 2 — server-side migration
- **Phase 4 (US3)**: Depends on Phase 3 — bot handler migration (handlers already import-clean after Phase 3 shims)
- **Phase 5 (US4)**: Depends on Phase 4 — `bot/utils/db.py` deletion (handlers already updated in Phase 4)
- **Phase 6 (US5)**: Depends on Phase 5 — test update (needs clean handlers)
- **Phase 7 (Polish)**: Depends on Phases 3–6

### Within Each Phase

- T002 and T003 (Phase 1) are parallel — different files
- T015–T020 (Phase 4) are parallel after T013+T014 — one file per handler
- T027–T030 (Phase 7) are parallel — read-only checks

### Parallel Opportunities

| Group | Tasks | Condition |
|-------|-------|-----------|
| Phase 1 package files | T002, T003 | After T001 |
| Phase 4 bot handlers | T015, T016, T017, T018, T019, T020 | After T013, T014 |
| Phase 7 grep audits | T027, T028, T029, T030 | After Phase 6 |

---

## Implementation Strategy

### Safe Incremental Migration

1. **Phase 1**: Build `db/` in isolation — no risk
2. **Phase 2**: Verify `db/` correct before touching anything
3. **Phase 3**: Migrate server via shims — API endpoints preserved throughout
4. **Phase 4**: Migrate bot handlers — bot commands preserved throughout
5. **Phase 5**: Delete `bot/utils/db.py` — only after handlers no longer use it
6. **Phase 6**: Update tests to use env-var DB override
7. **Phase 7**: Full audit and regression check

At every phase checkpoint, the system is in a working state. The migration never leaves the codebase broken mid-phase.

### Stop Points (validate before proceeding)

- After Phase 1 checkpoint: `from db import ...` works
- After Phase 2 checkpoint: DB round-trip confirmed
- After Phase 3 checkpoint: FastAPI server fully functional
- After Phase 4 checkpoint: Zero `bot_crud` references
- After Phase 5 checkpoint: Zero `sys.path` references
- After Phase 6 checkpoint: All 13 tests pass on in-memory DB

---

## Notes

- [P] tasks operate on different files — safe to run in parallel
- Shim files (`database.py`, `models.py`, `crud.py`) are intentionally left in place after this feature; they are not removed until a follow-up cleanup PR
- The `Base` import chain matters: declare `Base` in `db/models.py`, import it in `db/engine.py` — this avoids circular imports
- `NullPool` is in `sqlalchemy.pool` — import as `from sqlalchemy.pool import NullPool`
- Test fixture must set `DATABASE_URL` env var **before** importing from `db` — Python caches module state
