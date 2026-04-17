# Quickstart: Shared Database Layer

**Branch**: `002-shared-db-layer` | **Date**: 2026-04-16

## New Package Structure

```text
db/
├── __init__.py       # Public API exports
├── engine.py         # Engine, session factory, session utilities
├── models.py         # ORM models and enums (moved from backend/src/models.py)
└── repositories.py   # All query functions (merged from crud.py + bot_crud.py)
```

## Using the `db` Package

### In the API Server (FastAPI)

```python
# backend/src/main.py
from db import get_db, repositories
from sqlalchemy.orm import Session
from fastapi import Depends

@app.get("/inventory/")
def read_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repositories.get_all_dresses(db, skip=skip, limit=limit)
```

### In the Telegram Bot (async handler)

```python
# bot/handlers/stock.py
import asyncio
from db import get_session, repositories
from bot.utils.formatting import format_live_stock, split_message

async def stock_command(update, context):
    def _query():
        with get_session() as db:
            return repositories.get_live_stock(db)

    dresses = await asyncio.to_thread(_query)
    text = format_live_stock(dresses)
    for chunk in split_message(text):
        await update.message.reply_text(chunk, parse_mode="Markdown")
```

### In Tests

```python
import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from db import engine, Base, get_session, repositories

Base.metadata.create_all(bind=engine)

def test_get_live_stock():
    with get_session() as db:
        # seed data
        dress = ...
        db.add(dress)
        # Note: get_session() commits on exit — but in tests, use db.flush() before querying
        result = repositories.get_live_stock(db)
        assert len(result) == 1
```

> **Test note**: Set `DATABASE_URL=sqlite:///:memory:` before importing `db` to avoid touching the real database. Use `Base.metadata.create_all(bind=engine)` in fixtures.

## Environment Setup

```bash
# Development (default — uses ./inventory.db)
# No env var needed; inventory.db created by backend on first run

# Test isolation
export DATABASE_URL="sqlite:///:memory:"

# Production / alternative path
export DATABASE_URL="sqlite:////absolute/path/to/inventory.db"
```

## Files Deleted in This Refactor

| Deleted | Replaced By |
|---------|-------------|
| `backend/src/bot_crud.py` | `db/repositories.py` |
| `bot/utils/db.py` | `from db import get_session` |

## Files Kept as Transitional Shims

| Shim | Content | Remove when |
|------|---------|-------------|
| `backend/src/database.py` | `from db.engine import *` | All direct imports updated |
| `backend/src/models.py` | `from db.models import *` | All direct imports updated |
| `backend/src/crud.py` | `from db.repositories import *` | All direct imports updated |

## Verification Checklist

- [ ] `python -c "from db import get_session, repositories, DressInventory"` succeeds from project root
- [ ] `backend/venv/bin/python -m uvicorn backend.src.main:app` starts without import errors
- [ ] `backend/venv/bin/python -m bot.main` starts without import errors (token not needed to verify imports)
- [ ] `backend/venv/bin/python -m pytest bot/tests/ -v` — all tests pass
- [ ] No `sys.path` in any `.py` file: `grep -r "sys.path" . --include="*.py"` returns nothing
- [ ] Database config in one place: `grep -r "sqlite:///" . --include="*.py"` returns only `db/engine.py`
