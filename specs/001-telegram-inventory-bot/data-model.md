# Data Model: Telegram Inventory Bot

**Branch**: `001-telegram-inventory-bot` | **Date**: 2026-04-16

## Existing Entities (reused, not modified)

### DressInventory (`dress_inventory` table)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| item_id | Integer | PK, auto-increment | Used in `/status <item_id>` |
| model_number | String | NOT NULL | Used in `/dress <model>` and `/add` |
| size | String | NOT NULL | e.g., "36", "38", "40" |
| cup_size | Enum(CupSize) | NOT NULL | A / B / C / D |
| is_custom_sewing | Boolean | default False | |
| storage_location | Enum(StorageLocation) | NOT NULL | Tel Aviv / Ashdod / Abroad |
| dress_condition | Enum(DressCondition) | NOT NULL | Good / Laundry Damage / Replace Top / Replace Skirt |
| status | Enum(DressStatus) | NOT NULL | In Stock / Display / Abroad / In Sewing / Out to Bride |
| notes | String | nullable | |

**Live stock**: status IN (In Stock, Display)  
**Future stock (physical)**: status IN (In Sewing, Abroad, Out to Bride)

### ActiveOrder (`active_orders` table)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| order_id | Integer | PK, auto-increment | |
| model_number | String | NOT NULL | |
| bride_name | String | NOT NULL | Shown in `/orders` |
| first_measurement_date | Date | NOT NULL | |
| wedding_date | Date | NOT NULL | Used for future stock return date + `/orders [days]` filter |
| size | String | NOT NULL | |
| bust_cm | Float | NOT NULL | |
| hips_cm | Float | NOT NULL | |
| waist_cm | Float | NOT NULL | |
| cup_size | Enum(CupSize) | NOT NULL | |
| height_cm | Float | NOT NULL | |
| is_custom_sewing | Boolean | default False | |
| order_type | Enum(OrderType) | NOT NULL | Stock-based / New Order / Trunk-show |
| notes | String | nullable | |
| dress_id | Integer | FK → dress_inventory.item_id, nullable | Linked dress |

**Future stock (orders)**: order_type = New Order (custom dresses not yet physically in boutique)

## State Transitions: DressStatus

```
[New dress added] → In Stock
In Stock → Display          (put on floor display)
In Stock / Display → In Sewing     (sent for alterations)
In Stock / Display → Out to Bride  (lent to bride)
In Stock / Display → Abroad        (sent abroad)
In Sewing → In Stock        (returned from tailor)
Out to Bride → In Stock     (bride returned dress)
Abroad → In Stock           (returned from abroad)
```

Valid transitions are enforced at the application level; the bot allows any status → any status via `/status` but will reject invalid enum values.

## New Bot-Specific Query Functions (`backend/src/bot_crud.py`)

### `get_live_stock(db) → List[DressInventory]`
- Filter: `status IN ('In Stock', 'Display')`
- Order: `model_number ASC, size ASC`
- Returns: all matching dress records

### `get_future_stock(db) → dict`
- Returns: `{ "dresses": List[DressInventory], "new_orders": List[ActiveOrder] }`
- Dresses filter: `status IN ('In Sewing', 'Abroad', 'Out to Bride')`
- Orders filter: `order_type = 'New Order'`
- Dresses include their linked order (for wedding date) via join
- Order: dresses by status then model; new_orders by wedding_date ASC

### `get_dresses_by_model(db, model_number) → List[DressInventory]`
- Filter: `model_number = :model_number` (case-insensitive)
- Eagerly loads linked orders
- Order: `size ASC, cup_size ASC`

### `get_orders_filtered(db, days=None) → List[ActiveOrder]`
- If `days` provided: filter `wedding_date BETWEEN today AND today + days`
- Else: return all active orders
- Order: `wedding_date ASC`

### `update_dress_status(db, item_id, new_status) → DressInventory | None`
- Fetches dress by item_id; returns None if not found
- Validates new_status is a valid DressStatus enum value
- Updates and commits; returns updated record

### `add_dress(db, model_number, size, cup_size, location, condition='Good', notes=None) → DressInventory`
- Creates new DressInventory with status='In Stock' by default
- Validates enum values for cup_size, location, condition
- Returns created record
