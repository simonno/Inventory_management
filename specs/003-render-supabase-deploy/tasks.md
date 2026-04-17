# Tasks: Deploy to Render + Supabase

**Input**: Design documents from `/specs/003-render-supabase-deploy/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Organization**: Tasks grouped by user story — each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create root-level deployment artifacts and fix cross-cutting compatibility issues

- [x] T001 Create root `requirements.txt` combining backend + bot deps with `psycopg2-binary`, removing `aiosqlite` at `/Users/simonoam/PycharmProjects/Inventory_management/requirements.txt`
- [x] T002 Fix `db/engine.py` — make `connect_args={"check_same_thread": False}` conditional on SQLite, so Postgres connections work correctly

**Checkpoint**: Shared infra ready — all user stories can now proceed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify Postgres compatibility and frontend build work before deploying

- [x] T003 Verify SQLAlchemy models in `db/models.py` use no SQLite-specific column types (run `python -c "from db.models import Base; print(Base.metadata.tables)"` successfully)
- [x] T004 Build React frontend: run `cd frontend && npm install && npm run build` and confirm `frontend/dist/index.html` exists

**⚠️ CRITICAL**: Both checks must pass before user story implementation can begin

**Checkpoint**: Foundation verified — Postgres-compatible models and built frontend confirmed

---

## Phase 3: User Story 1 — App is live and accessible (Priority: P1) 🎯 MVP

**Goal**: FastAPI serves the React frontend + REST API from a single Render web service connected to Supabase

**Independent Test**: Run `uvicorn backend.src.main:app` from repo root → visit `http://localhost:8000` → React UI loads; visit `http://localhost:8000/inventory/` → JSON API responds

### Implementation

- [x] T005 [US1] Add static file serving to `backend/src/main.py` — import `StaticFiles`, remove `read_root()` route, mount `frontend/dist` at `"/"` after all API routes
- [x] T006 [US1] Test static serving locally: run `uvicorn backend.src.main:app --host 0.0.0.0 --port 8000` from repo root, confirm `http://localhost:8000` returns React UI and `http://localhost:8000/inventory/` returns JSON

**Checkpoint**: US1 complete — single service serves both frontend and API locally

---

## Phase 4: User Story 3 — Database connects to Supabase (Priority: P1)

**Goal**: Both services connect to Supabase Postgres via `DATABASE_URL` env var; no SQLite in production

**Independent Test**: Set `DATABASE_URL=postgresql://...` locally → start FastAPI → tables auto-created in Supabase → add item via API → item persists in Supabase

### Implementation

- [x] T007 [US3] Write integration smoke test in `db/tests/test_engine_postgres_compat.py` — assert engine URL scheme starts with `postgresql` when `DATABASE_URL` env var is set to a postgres URL, and that `check_same_thread` is not passed as connect arg
- [x] T008 [US3] Run smoke test: `python -m pytest db/tests/test_engine_postgres_compat.py -v` — confirm it passes after T002 fix

**Checkpoint**: US3 complete — DB layer is Postgres-ready and validated

---

## Phase 5: User Story 2 — Telegram bot always-on (Priority: P2)

**Goal**: Bot runs as a Render worker, stays alive, reads/writes to Supabase

**Independent Test**: `python -m bot.main` starts without errors when `TELEGRAM_BOT_TOKEN` and `DATABASE_URL` are set; send `/stock` command and receive inventory list from Supabase

### Implementation

- [x] T009 [P] [US2] Verify bot entry point: run `python -c "import bot.main; print('OK')"` from repo root — confirm no import errors
- [x] T010 [US2] Create `render.yaml` at repo root with web service (FastAPI + frontend build) and worker (bot polling) definitions including env var declarations for `DATABASE_URL` and `TELEGRAM_BOT_TOKEN`

**Checkpoint**: US2 complete — render.yaml declares both services with correct build/start commands

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, commit, and deploy readiness

- [x] T011 [P] Verify `render.yaml` is valid YAML: `python -c "import yaml; yaml.safe_load(open('render.yaml'))"` — no errors
- [x] T012 [P] Verify `.gitignore` excludes `frontend/dist/` and `*.db` files — add patterns if missing
- [x] T013 Commit all changes: `git add db/engine.py backend/src/main.py requirements.txt render.yaml && git commit -m "feat: deploy to Render with Supabase Postgres"`
- [ ] T014 Push branch and follow `quickstart.md` steps to deploy on Render with Supabase `DATABASE_URL` and `TELEGRAM_BOT_TOKEN` set as environment variables

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — blocks all user stories
- **US1, US3 (Phase 3, 4)**: Both depend on Foundational — can run in parallel
- **US2 (Phase 5)**: Depends on Phase 1 (requirements.txt) — can run after foundational
- **Polish (Phase 6)**: Depends on all phases complete

### Parallel Opportunities

- T005 (static files) and T007 (DB smoke test) can run in parallel after Phase 2
- T009 (bot import check) can run in parallel with any Phase 3/4 task
- T011 and T012 (validation) can run in parallel in Phase 6

---

## Implementation Strategy

### MVP First (US1 + US3 — minimum to go live)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003, T004)
3. Complete Phase 3: US1 static serving (T005, T006)
4. Complete Phase 4: US3 DB compatibility (T007, T008)
5. Complete Phase 5: US2 render.yaml (T009, T010)
6. **STOP and VALIDATE** locally before deploying
7. Complete Phase 6: Polish + deploy (T011–T014)

---

## Notes

- No data migration needed — fresh Supabase DB, tables created by SQLAlchemy on first start
- Local dev still works with SQLite fallback (no `DATABASE_URL` set)
- `render.yaml` uses `sync: false` env vars — Render will prompt for values on first deploy
- Cold start on free Render web service is expected and acceptable for this internal tool
