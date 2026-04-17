# Contract: `db` Package Public API

**Branch**: `002-shared-db-layer` | **Date**: 2026-04-16

This document defines the public interface contract for the `db` package. Any consumer (API server, Telegram bot, tests) MUST interact with the database exclusively through this interface.

---

## Top-Level Exports (`from db import ...`)

| Name | Type | Description |
|------|------|-------------|
| `engine` | `sqlalchemy.Engine` | Configured SQLAlchemy engine |
| `SessionLocal` | `sessionmaker` | Session factory — use `get_session()` instead for lifecycle safety |
| `get_session` | `contextmanager` | Safe sync session context manager |
| `get_db` | `generator` | FastAPI Depends-compatible session provider |
| `Base` | `DeclarativeBase` | SQLAlchemy declarative base — used for `Base.metadata.create_all()` |
| `DressInventory` | ORM model | Dress record |
| `ActiveOrder` | ORM model | Bride order record |
| `CupSize` | Enum | A / B / C / D |
| `OrderType` | Enum | Stock-based / New Order / Trunk-show |
| `StorageLocation` | Enum | Tel Aviv / Ashdod / Abroad |
| `DressCondition` | Enum | Good / Laundry Damage / Replace Top / Replace Skirt |
| `DressStatus` | Enum | In Stock / Display / Abroad / In Sewing / Out to Bride |
| `repositories` | module | All query functions |

---

## `get_session()` Contract

```python
from db import get_session, repositories

with get_session() as db:
    dresses = repositories.get_live_stock(db)
```

**Guarantees**:
- Yields exactly one `Session` instance
- Commits if the `with` block exits without exception
- Rolls back if the `with` block raises any exception
- Always closes the session on exit (no leak)
- Thread-safe: each call creates an independent session

**Usage context**: Sync callers — bot handlers (via `asyncio.to_thread`), scripts, tests.

---

## `get_db()` Contract

```python
from db import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

def endpoint(db: Session = Depends(get_db)):
    return repositories.get_all_dresses(db)
```

**Guarantees**: Identical lifecycle to `get_session()` — commit on success, rollback on exception, always close.

**Usage context**: FastAPI route functions only. Do NOT use in bot handlers or tests.

---

## `repositories` Module Contract

All repository functions follow this convention:

- First argument is always `db: Session`
- Return type is always typed
- Raise `ValueError` (not HTTP exceptions) for invalid input — callers handle presentation
- Return `None` for not-found cases (no exceptions for missing records)
- Never commit or rollback inside a repository function — session lifecycle is the caller's responsibility

### Dress Functions

```python
repositories.get_all_dresses(db, skip=0, limit=100) -> List[DressInventory]
repositories.create_dress(db, dress: DressInventoryCreate) -> DressInventory
repositories.get_live_stock(db) -> List[DressInventory]
repositories.get_future_stock(db) -> dict  # {"dresses": [...], "new_orders": [...]}
repositories.get_dresses_by_model(db, model_number: str) -> List[DressInventory]
repositories.update_dress_status(db, item_id: int, new_status: str) -> DressInventory | None
repositories.add_dress(db, model_number, size, cup_size, location, condition='Good', notes=None) -> DressInventory
```

### Order Functions

```python
repositories.get_all_orders(db, skip=0, limit=100) -> List[ActiveOrder]
repositories.create_order(db, order: ActiveOrderCreate) -> ActiveOrder
repositories.link_order_to_dress(db, order_id: int, dress_id: int) -> ActiveOrder | None
repositories.get_orders_filtered(db, days: int | None = None) -> List[ActiveOrder]
```

---

## Environment Configuration Contract

| Variable | Required | Default | Effect |
|----------|----------|---------|--------|
| `DATABASE_URL` | No | `sqlite:///./inventory.db` | Database connection string |

**Behaviour if `DATABASE_URL` not set**: Connects to `./inventory.db` relative to the working directory; logs `WARNING: DATABASE_URL not set, using default sqlite:///./inventory.db`.

**Test override pattern**:
```python
import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
```

---

## What Is NOT Part of the Public API

The following are internal implementation details and MUST NOT be imported directly by consumers:

- `db.engine.SessionLocal` (use `get_session()` or `get_db()` instead)
- Any internal helpers inside `db/engine.py` beyond the listed exports
- The `db/models.py` module path (import from `db` top-level, not `db.models`)
- The `db/repositories.py` module path (import as `from db import repositories`)
