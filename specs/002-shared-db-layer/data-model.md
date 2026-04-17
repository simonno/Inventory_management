# Data Model: Shared Database Layer

**Branch**: `002-shared-db-layer` | **Date**: 2026-04-16

## Package Public Interface (`db/__init__.py`)

The `db` package exposes the following names at the top level:

```python
from db import engine, SessionLocal, get_session, get_db   # engine & session utilities
from db import Base                                         # declarative base
from db import DressInventory, ActiveOrder                  # ORM models
from db import CupSize, OrderType, StorageLocation, DressCondition, DressStatus  # enums
from db import repositories                                 # query functions module
```

## Module: `db/engine.py`

### Configuration

| Variable | Source | Default | Notes |
|----------|--------|---------|-------|
| `DATABASE_URL` | `os.environ` | `sqlite:///./inventory.db` | Warns if default used |

### Engine Setup

```
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

`NullPool` is used for SQLite to prevent "database is locked" errors under concurrent writes from the bot and server. For in-memory SQLite (tests), callers pass `StaticPool` via override.

### Session Utilities

#### `get_session()` — Context Manager (sync callers)

```
with get_session() as db:
    result = repositories.get_live_stock(db)
```

Behaviour:
- Yields a `Session`
- On exit without exception: `db.commit()`
- On exit with exception: `db.rollback()`
- Always: `db.close()`

#### `get_db()` — FastAPI Dependency Generator

```python
def endpoint(db: Session = Depends(get_db)):
    ...
```

Behaviour: identical lifecycle to `get_session()`, expressed as a generator for FastAPI's dependency injection.

## Module: `db/models.py`

Moved verbatim from `backend/src/models.py`. No schema changes.

### Enums

| Enum | Values |
|------|--------|
| `CupSize` | A, B, C, D |
| `OrderType` | Stock-based, New Order, Trunk-show |
| `StorageLocation` | Tel Aviv, Ashdod, Abroad |
| `DressCondition` | Good, Laundry Damage, Replace Top, Replace Skirt |
| `DressStatus` | In Stock, Display, Abroad, In Sewing, Out to Bride |

### ORM Models

#### `DressInventory` (table: `dress_inventory`)

| Column | Type | Constraints |
|--------|------|-------------|
| item_id | Integer | PK, auto-increment |
| model_number | String | NOT NULL |
| size | String | NOT NULL |
| cup_size | Enum(CupSize) | NOT NULL |
| is_custom_sewing | Boolean | default False |
| storage_location | Enum(StorageLocation) | NOT NULL |
| dress_condition | Enum(DressCondition) | NOT NULL |
| status | Enum(DressStatus) | NOT NULL |
| notes | String | nullable |

Relationship: `orders → List[ActiveOrder]` (back_populates="dress")

#### `ActiveOrder` (table: `active_orders`)

| Column | Type | Constraints |
|--------|------|-------------|
| order_id | Integer | PK, auto-increment |
| model_number | String | NOT NULL |
| bride_name | String | NOT NULL |
| first_measurement_date | Date | NOT NULL |
| wedding_date | Date | NOT NULL |
| size | String | NOT NULL |
| bust_cm | Float | NOT NULL |
| hips_cm | Float | NOT NULL |
| waist_cm | Float | NOT NULL |
| cup_size | Enum(CupSize) | NOT NULL |
| height_cm | Float | NOT NULL |
| is_custom_sewing | Boolean | default False |
| order_type | Enum(OrderType) | NOT NULL |
| notes | String | nullable |
| dress_id | Integer | FK → dress_inventory.item_id, nullable |

Relationship: `dress → DressInventory` (back_populates="orders")

## Module: `db/repositories.py`

All query functions. Signature convention: `function_name(db: Session, ...) -> ReturnType`.

### Dress Queries

| Function | Signature | Returns | Notes |
|----------|-----------|---------|-------|
| `get_all_dresses` | `(db, skip=0, limit=100)` | `List[DressInventory]` | Replaces `crud.get_dress_inventory` |
| `create_dress` | `(db, dress: DressInventoryCreate)` | `DressInventory` | Replaces `crud.create_dress_inventory` |
| `get_live_stock` | `(db)` | `List[DressInventory]` | From `bot_crud`; status IN_STOCK or DISPLAY, ordered by model/size |
| `get_future_stock` | `(db)` | `dict` | From `bot_crud`; returns `{"dresses": [...], "new_orders": [...]}` |
| `get_dresses_by_model` | `(db, model_number: str)` | `List[DressInventory]` | From `bot_crud`; case-insensitive |
| `update_dress_status` | `(db, item_id: int, new_status: str)` | `DressInventory \| None` | From `bot_crud`; raises `ValueError` on invalid status |
| `add_dress` | `(db, model_number, size, cup_size, location, condition='Good', notes=None)` | `DressInventory` | From `bot_crud`; validates enums, default status IN_STOCK |

### Order Queries

| Function | Signature | Returns | Notes |
|----------|-----------|---------|-------|
| `get_all_orders` | `(db, skip=0, limit=100)` | `List[ActiveOrder]` | Replaces `crud.get_active_orders` |
| `create_order` | `(db, order: ActiveOrderCreate)` | `ActiveOrder` | Replaces `crud.create_active_order` |
| `link_order_to_dress` | `(db, order_id: int, dress_id: int)` | `ActiveOrder \| None` | From `crud`; returns None if order not found |
| `get_orders_filtered` | `(db, days: int \| None = None)` | `List[ActiveOrder]` | From `bot_crud`; optional wedding date window |

## Shim Files (Transitional)

### `backend/src/database.py` (shim)

```python
from db.engine import engine, SessionLocal, get_db
__all__ = ["engine", "SessionLocal", "get_db"]
```

### `backend/src/models.py` (shim)

```python
from db.models import *
```

Both shims are marked `# TRANSITIONAL: remove once all imports updated` and are slated for deletion in a follow-up cleanup PR.

## Migration Map

| Old import | New import |
|------------|-----------|
| `from backend.src.database import get_db` | `from db.engine import get_db` |
| `from .database import get_db` (inside backend) | `from db.engine import get_db` |
| `from .models import DressInventory` (inside backend) | `from db.models import DressInventory` |
| `from backend.src import bot_crud` | `from db import repositories` |
| `from bot.utils.db import get_db_session` | `from db.engine import get_session` |
| `sys.path.insert(...)` in `bot/utils/db.py` | **deleted** |
