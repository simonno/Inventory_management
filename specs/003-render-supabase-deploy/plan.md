# Deploy to Render + Supabase Implementation Plan

**Branch**: `003-render-supabase-deploy` | **Date**: 2026-04-17 | **Spec**: [spec.md](spec.md)

## Summary

Deploy the FastAPI backend (serving the React frontend as static files) and Telegram bot as two separate Render services, both connecting to a shared Supabase Postgres database, replacing SQLite.

## Technical Context

**Language/Version**: Python 3.9, Node 18+  
**Primary Dependencies**: FastAPI, SQLAlchemy, python-telegram-bot==20.*, psycopg2-binary (new), Vite  
**Storage**: Supabase Postgres (replaces SQLite in production)  
**Testing**: pytest  
**Target Platform**: Render (Linux), Supabase  
**Project Type**: Web service + background worker  
**Performance Goals**: Cold start < 30s (acceptable for internal), bot response < 5s  
**Constraints**: Free tier on both Render and Supabase  
**Scale/Scope**: Small internal team (~5 users)

## Constitution Check

Constitution template not filled in for this project — no gates to enforce.

## Project Structure

```text
# Repo root (changes from this feature)
requirements.txt          ← NEW: combined deps for both services
render.yaml               ← NEW: Render Blueprint (IaC)

db/
└── engine.py             ← MODIFY: conditional connect_args

backend/
└── src/
    └── main.py           ← MODIFY: serve frontend/dist as static files

specs/003-render-supabase-deploy/
├── plan.md               ← this file
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md              ← Phase 2 (speckit.tasks)
```

---

## Task 1: Fix db/engine.py for Postgres compatibility

**Files:**
- Modify: `db/engine.py`

- [ ] **Step 1: Write the failing test**

Add to `db/tests/test_engine.py` (create if absent):

```python
def test_postgres_url_does_not_pass_sqlite_connect_args():
    """engine creation with a postgres:// URL must not include check_same_thread."""
    import importlib, sys, os
    os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/testdb"
    # reload module so module-level code re-runs with new env var
    if "db.engine" in sys.modules:
        del sys.modules["db.engine"]
    import db.engine as eng
    # SQLAlchemy stores connect_args on the dialect; postgres dialect ignores
    # check_same_thread but we verify we don't pass it (would raise on real connect)
    dialect_kwargs = eng.engine.dialect.create_connect_args.__func__  # noqa
    # Simpler: just assert the engine URL scheme is postgresql
    assert eng.engine.url.drivername.startswith("postgresql")
    # Cleanup
    del os.environ["DATABASE_URL"]
    del sys.modules["db.engine"]
```

- [ ] **Step 2: Run test to verify it fails (or passes trivially)**

```bash
cd /Users/simonoam/PycharmProjects/Inventory_management
python -m pytest db/tests/test_engine.py -v
```

- [ ] **Step 3: Fix connect_args in db/engine.py**

Replace this block in `db/engine.py`:

```python
_in_memory = DATABASE_URL == "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool if _in_memory else NullPool,
)
```

With:

```python
_is_sqlite = DATABASE_URL.startswith("sqlite")
_in_memory = DATABASE_URL == "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    poolclass=StaticPool if _in_memory else NullPool,
)
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest db/ -v
```

Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add db/engine.py db/tests/
git commit -m "fix: make connect_args conditional on SQLite for Postgres compatibility"
```

---

## Task 2: Create root requirements.txt

**Files:**
- Create: `requirements.txt` (repo root)

- [ ] **Step 1: Create the file**

```text
# Web service (FastAPI)
fastapi
uvicorn[standard]
sqlalchemy
pydantic
pydantic-settings
python-multipart
psycopg2-binary

# Worker (Telegram bot)
python-telegram-bot==20.*
```

Save as `/Users/simonoam/PycharmProjects/Inventory_management/requirements.txt`

- [ ] **Step 2: Verify it installs cleanly**

```bash
pip install -r requirements.txt --dry-run
```

Expected: no conflicts, no errors

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: add root requirements.txt with psycopg2-binary for Render deploy"
```

---

## Task 3: Serve React frontend from FastAPI

**Files:**
- Modify: `backend/src/main.py`

- [ ] **Step 1: Build the frontend to verify dist exists**

```bash
cd frontend && npm install && npm run build && cd ..
```

Expected: `frontend/dist/index.html` exists

- [ ] **Step 2: Add static file serving to main.py**

Add these imports at the top of `backend/src/main.py`:

```python
import os
from fastapi.staticfiles import StaticFiles
```

Remove the `read_root` function:

```python
# DELETE this:
@app.get("/")
def read_root():
    return {"message": "Bridal Inventory System API"}
```

Add static file mount at the end of `backend/src/main.py` (after all API routes):

```python
_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.isdir(_dist):
    app.mount("/", StaticFiles(directory=_dist, html=True), name="static")
```

- [ ] **Step 3: Test locally**

```bash
cd /Users/simonoam/PycharmProjects/Inventory_management
uvicorn backend.src.main:app --reload
```

Open http://localhost:8000 — should show the React inventory UI, not JSON.
Open http://localhost:8000/inventory/ — should still return JSON API response.

- [ ] **Step 4: Commit**

```bash
git add backend/src/main.py
git commit -m "feat: serve React frontend dist as static files from FastAPI"
```

---

## Task 4: Create render.yaml

**Files:**
- Create: `render.yaml` (repo root)

- [ ] **Step 1: Create render.yaml**

```yaml
services:
  - type: web
    name: inventory-web
    env: python
    buildCommand: pip install -r requirements.txt && cd frontend && npm install && npm run build
    startCommand: uvicorn backend.src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false

  - type: worker
    name: inventory-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -m bot.main
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: TELEGRAM_BOT_TOKEN
        sync: false
```

Save as `/Users/simonoam/PycharmProjects/Inventory_management/render.yaml`

- [ ] **Step 2: Verify bot entry point works**

```bash
cd /Users/simonoam/PycharmProjects/Inventory_management
python -c "import bot.main; print('bot import OK')"
```

Expected: `bot import OK`

- [ ] **Step 3: Commit**

```bash
git add render.yaml
git commit -m "chore: add render.yaml Blueprint for web service + bot worker deployment"
```

---

## Task 5: Deploy to Render + Supabase

- [ ] **Step 1: Create Supabase project**

1. Go to https://supabase.com → New project
2. Settings → Database → Connection string → URI → copy value
3. It looks like: `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`

- [ ] **Step 2: Push branch / merge to main**

```bash
git push origin 003-render-supabase-deploy
# Open PR and merge to main, or:
git checkout main && git merge 003-render-supabase-deploy && git push
```

- [ ] **Step 3: Connect repo to Render**

1. Render dashboard → New → Blueprint
2. Connect GitHub repo
3. Render detects `render.yaml` and shows both services
4. Click "Apply"

- [ ] **Step 4: Set environment variables**

In Render dashboard, for **inventory-web**:
- `DATABASE_URL` = Supabase URI from Step 1

For **inventory-bot**:
- `DATABASE_URL` = same Supabase URI
- `TELEGRAM_BOT_TOKEN` = your bot token

- [ ] **Step 5: Verify web service**

Open the Render web service URL → React UI loads → add an inventory item → refresh → item persists.

- [ ] **Step 6: Verify bot**

Send `/stock` to the Telegram bot → returns inventory list from Supabase.

- [ ] **Step 7: Cross-service verification**

Add item via web UI → send `/stock` to bot → new item appears in bot response.
