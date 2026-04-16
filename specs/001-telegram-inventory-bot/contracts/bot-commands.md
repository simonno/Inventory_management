# Bot Command Contract

**Branch**: `001-telegram-inventory-bot` | **Date**: 2026-04-16

This document defines the complete slash command interface for the Telegram Inventory Bot. It serves as the contract between the bot implementation and the Telegram BotFather `/setcommands` registration.

## Command Definitions

### `/stock`

**Purpose**: Show all dresses currently available in the boutique.

**Arguments**: None

**Trigger**: User sends `/stock`

**Response format**:
```
📦 Live Stock

*Model 1234*
  • Size 38, Cup B — Tel Aviv — Good
  • Size 40, Cup C — Ashdod — Good ⚠️ Replace Top

*Model 5678*
  • Size 36, Cup A — Tel Aviv — Good

Total: 3 dresses in stock
```

**Grouping**: By model number (alphabetical). Each dress on its own line showing size, cup size, location, condition. Condition flag `⚠️` shown if not "Good".

**Empty state**: "No dresses currently in stock."

---

### `/future`

**Purpose**: Show all dresses and orders expected to arrive or return.

**Arguments**: None

**Trigger**: User sends `/future`

**Response format**:
```
🔮 Future Stock

*In Sewing*
  • #12 Model 1234, Size 38, Cup B → return est. unknown

*Out to Bride*
  • #7 Model 5678, Size 36, Cup A → wedding 2026-05-10 (bride: Sarah)

*Abroad*
  • #15 Model 9999, Size 40, Cup C → return est. unknown

*New Orders (not yet received)*
  • Order #42 — Model 2222, Size 38, Cup B — Sarah Cohen — wedding 2026-06-01
```

**Grouping**: By category (In Sewing → Out to Bride → Abroad → New Orders). Within each, sorted by expected date if available.

**Empty state**: "All inventory is currently in-house. No future stock pending."

---

### `/dress <model_number>`

**Purpose**: Show all inventory records for a specific dress model.

**Arguments**:
- `model_number` (required): The dress model number string. May contain digits, letters, hyphens.

**Trigger**: User sends `/dress 1234`

**Response format**:
```
👗 Model 1234

*#7* Size 36, Cup A — Tel Aviv — In Stock — Good
*#12* Size 38, Cup B — Ashdod — In Sewing — Good
   └ Linked order: Sarah Cohen, wedding 2026-05-10

Total: 2 records
```

**Error**: "No dresses found with model number '1234'."

**Missing argument**: "Usage: /dress <model_number>  Example: /dress 1234"

---

### `/orders [days]`

**Purpose**: List all active orders, optionally filtered to those with upcoming weddings.

**Arguments**:
- `days` (optional integer): If provided, show only orders with wedding_date within the next N days.

**Trigger**: `/orders` or `/orders 30`

**Response format**:
```
📋 Active Orders (next 30 days)

1. Sarah Cohen — Model 1234, Size 38, Cup B — wedding 2026-05-01 [Stock-based]
2. Dana Levy — Model 5678, Size 36, Cup A — wedding 2026-05-15 [New Order]

Total: 2 orders
```

**Sorted by**: wedding_date ascending (soonest first).

**Invalid days value**: "Days must be a positive number. Example: /orders 30"

**Empty state**: "No active orders found." or "No orders with weddings in the next 30 days."

---

### `/status <item_id> <new_status>`

**Purpose**: Update the status of a dress record.

**Arguments**:
- `item_id` (required integer): The dress's item_id from the database.
- `new_status` (required string): One of the valid status values (case-insensitive).

**Valid status values**: `in stock`, `display`, `abroad`, `in sewing`, `out to bride`

**Trigger**: `/status 7 "in sewing"` or `/status 7 in sewing`

**Response format**:
```
✅ Updated Dress #7

Model: 1234 | Size: 38 | Cup: B
Status: In Stock → In Sewing
Location: Tel Aviv
```

**Error — item not found**: "Dress #99 not found. Use /dress <model> to look up item IDs."

**Error — invalid status**: 
```
Invalid status 'foo'. Valid options:
  • in stock
  • display  
  • abroad
  • in sewing
  • out to bride
```

**Missing arguments**: "Usage: /status <item_id> <new_status>  Example: /status 7 in sewing"

---

### `/add <model> <size> <cup> <location>`

**Purpose**: Add a new dress to the inventory (initial status: In Stock).

**Arguments**:
- `model` (required): Model number string
- `size` (required): Size string (e.g., 36, 38, 40)
- `cup` (required): Cup size — one of A, B, C, D
- `location` (required): Storage location — one of `tel aviv`, `ashdod`, `abroad`

**Optional (prompted interactively or appended)**:
- `condition` defaults to `Good` if omitted
- `notes` not supported in v1 CLI form; add via web interface

**Trigger**: `/add 1234 38 B "tel aviv"`

**Response format**:
```
✅ Dress Added

#23 Model 1234, Size 38, Cup B
Status: In Stock | Location: Tel Aviv | Condition: Good
```

**Error — invalid enum**:
```
Invalid cup size 'E'. Valid options: A, B, C, D
```
```
Invalid location 'paris'. Valid options: tel aviv, ashdod, abroad
```

**Missing arguments**: "Usage: /add <model> <size> <cup> <location>  Example: /add 1234 38 B \"tel aviv\""

---

### `/help`

**Purpose**: Display all available commands with brief descriptions.

**Arguments**: None

**Trigger**: `/help` or any unrecognized input

**Response format**:
```
🤖 Bridal Inventory Bot — Commands

/stock — Show all available dresses (In Stock & Display)
/future — Show dresses expected back + new orders pending
/dress <model> — Look up all records for a model number
/orders [days] — List active orders (optional: next N days)
/status <id> <status> — Update a dress status
/add <model> <size> <cup> <location> — Add a new dress
/help — Show this help message
```

---

## BotFather `/setcommands` Registration

```
stock - Show all available dresses in stock
future - Show dresses expected back and new orders
dress - Look up a dress model: /dress <model_number>
orders - List active orders: /orders or /orders <days>
status - Update dress status: /status <item_id> <new_status>
add - Add a new dress: /add <model> <size> <cup> <location>
help - Show all available commands
```

## Error Handling Contract

All commands follow this error response pattern:
1. State what went wrong (specific, not generic)
2. Show correct usage syntax
3. Show a concrete example

Unrecognized input: "Unknown command. Send /help to see available commands."
Backend unavailable: "⚠️ Could not reach the inventory database. Please try again in a moment."
