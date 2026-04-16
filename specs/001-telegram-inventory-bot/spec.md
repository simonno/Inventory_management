# Feature Specification: Telegram Inventory Management Bot

**Feature Branch**: `001-telegram-inventory-bot`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: User description: "create a bot Telegram, that could vie chat, managing inventory"

## Clarifications

### Session 2026-04-16

- Q: What interaction model should the bot use — natural language, slash commands, or both? → A: Slash commands only (simpler for first deployment; natural language deferred to a future version).
- Q: Should the bot support adding/removing dress records, or just reading and status updates? → A: Allow adding a new dress via `/add`; deletion and order creation stay in the web interface only.
- Q: Who can make write changes via the bot — all users or restricted roles? → A: All authorized users have full read and write access; no role separation in v1.
- Q: How should `/stock` and `/future` group and display results? → A: Group by model number; list each size/cup-size as a sub-item underneath each model.
- Q: What does "future stock" include — only physical dresses expected back, or also new orders and trunk-show returns? → A: All of the above — dresses In Sewing, Abroad, Out to Bride, Trunk-show returns, and New Order type orders not yet received.

## Domain Context

This bot manages a **bridal dress inventory** for a boutique. The data model has two core entities:

- **Dress** (`dress_inventory`): individual physical dress identified by model number, size, cup size, storage location (Tel Aviv / Ashdod / Abroad), dress condition, and status (In Stock / Display / Abroad / In Sewing / Out to Bride). May be linked to an active order.
- **Order** (`active_orders`): a bride's order linked to a dress or to a new-order request, containing bride name, wedding date, body measurements, and order type (Stock-based / New Order / Trunk-show).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Live Stock via `/stock` (Priority: P1)

A user sends `/stock` and the bot replies with all dresses currently available (status: In Stock or Display), grouped by model number, showing size, cup size, and storage location.

**Why this priority**: Knowing what is physically available right now is the most frequent day-to-day query for the team.

**Independent Test**: Can be fully tested by calling `/stock` and verifying the response lists only dresses with status In Stock or Display, matching the database contents.

**Acceptance Scenarios**:

1. **Given** dresses with status In Stock or Display exist, **When** the user sends `/stock`, **Then** the bot replies with a grouped list showing model, size, cup size, location, and condition.
2. **Given** no dresses are currently available, **When** the user sends `/stock`, **Then** the bot replies with a message indicating no dresses are currently in stock.
3. **Given** a dress has condition Laundry Damage or Replace Top/Skirt, **When** it appears in the stock list, **Then** its condition is clearly flagged so the team knows it needs attention.

---

### User Story 2 - View Future Stock via `/future` (Priority: P1)

A user sends `/future` and the bot replies with all dresses currently unavailable but expected to return or arrive — those with status In Sewing, Abroad, or Out to Bride — along with any linked orders showing expected return dates (wedding dates for Out to Bride dresses).

**Why this priority**: Knowing what stock is coming back is essential for committing new dresses to brides and planning purchasing.

**Independent Test**: Can be fully tested by calling `/future` and verifying only dresses with status In Sewing, Abroad, or Out to Bride are shown, with their associated order/wedding date where available.

**Acceptance Scenarios**:

1. **Given** dresses with status In Sewing, Abroad, or Out to Bride exist, **When** the user sends `/future`, **Then** the bot lists them grouped by status, showing model, size, cup size, and expected availability date where known.
2. **Given** a dress is Out to Bride with a linked order, **When** listed under `/future`, **Then** the bride's wedding date is shown as the expected return date.
3. **Given** no dresses are currently out, **When** the user sends `/future`, **Then** the bot confirms all inventory is currently in-house.

---

### User Story 3 - Look Up a Specific Dress via `/dress` (Priority: P2)

A user sends `/dress <model_number>` and the bot returns all items in inventory matching that model number, with full detail (all sizes, cup sizes, statuses, locations, conditions, and linked orders if any).

**Why this priority**: The team frequently needs to check whether a specific model is available in a bride's size before showing it.

**Independent Test**: Can be fully tested by calling `/dress <model>` for a known model and verifying all matching dresses and their linked orders appear.

**Acceptance Scenarios**:

1. **Given** a model number exists in inventory, **When** the user sends `/dress <model_number>`, **Then** the bot replies with all matching dress records and their current statuses.
2. **Given** a model number has active orders linked, **When** the user queries that model, **Then** the bot also shows which orders are linked and their wedding dates.
3. **Given** the model number does not exist, **When** the user queries it, **Then** the bot responds that no dresses with that model number were found.

---

### User Story 4 - View Active Orders via `/orders` (Priority: P2)

A user sends `/orders` (optionally filtered by upcoming wedding date range) and the bot lists all active orders with bride name, model, wedding date, and order type.

**Why this priority**: Order tracking is critical for sewing timeline and dress reservation management.

**Independent Test**: Can be fully tested by calling `/orders` and verifying all orders in `active_orders` are shown with correct bride names, models, and dates.

**Acceptance Scenarios**:

1. **Given** active orders exist, **When** the user sends `/orders`, **Then** the bot lists all orders sorted by wedding date (soonest first), showing bride name, model, size, order type, and wedding date.
2. **Given** the user sends `/orders 30`, **When** the bot processes the request, **Then** only orders with a wedding date within the next 30 days are shown.
3. **Given** no active orders exist, **When** the user sends `/orders`, **Then** the bot confirms there are no active orders.

---

### User Story 5 - Update Dress Status via `/status` (Priority: P2)

A user sends `/status <item_id> <new_status>` to change a dress's status (e.g., marking it as In Sewing after sending it to a tailor). The bot confirms the change.

**Why this priority**: Status changes drive both the live and future stock views; keeping them accurate is essential.

**Independent Test**: Can be tested by changing a dress status and verifying the updated status appears in `/stock` or `/future` as appropriate.

**Acceptance Scenarios**:

1. **Given** a valid item ID and a valid status value, **When** the user sends `/status <id> <status>`, **Then** the dress status is updated and the bot confirms with the dress details.
2. **Given** an invalid status value is provided, **When** the bot processes the command, **Then** the bot replies with an error listing valid status options.
3. **Given** the item ID does not exist, **When** the user sends the command, **Then** the bot informs the user the dress was not found.

---

### User Story 6 - Get Help via `/help` (Priority: P1)

A user sends `/help` and receives a clear list of all available commands with brief descriptions and usage examples.

**Why this priority**: With slash-command-only interaction, discoverability depends entirely on `/help` being clear and complete.

**Independent Test**: Can be tested by sending `/help` and verifying all available commands are listed with accurate descriptions.

**Acceptance Scenarios**:

1. **Given** any user sends `/help`, **When** the bot processes the request, **Then** the bot replies with a formatted list of all commands, their arguments, and one-line descriptions.
2. **Given** the user sends an unrecognized command, **When** the bot cannot match it, **Then** the bot replies with "Unknown command. Send /help to see available commands."

---

### Edge Cases

- What happens when a model number contains spaces or special characters in a slash command argument?
- How does the bot handle a `/future` query when a dress is Abroad with no linked order (no known return date)?
- What happens if a user tries to set a dress status to the same status it already has?
- How does the bot split a very long `/stock` or `/orders` response that exceeds Telegram message length limits (4096 characters)?
- What happens when the backend database is temporarily unreachable?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The bot MUST support slash commands as the exclusive interaction interface; no natural language processing is required in v1.
- **FR-002**: Users MUST be able to view all currently available dresses (status: In Stock or Display) via `/stock`. Results MUST be grouped by model number, with each size and cup size listed as sub-items under the model, showing storage location and condition.
- **FR-003**: Users MUST be able to view all dresses expected to return or arrive via `/future`. This includes: dresses with status In Sewing, Abroad, Out to Bride, and Trunk-show (physical dresses out of the boutique), plus any New Order type orders representing custom dresses not yet received. Expected return/arrival dates MUST be shown where available (e.g., wedding date for Out to Bride dresses).
- **FR-004**: Users MUST be able to look up all inventory records for a specific model number via `/dress <model_number>`.
- **FR-005**: Users MUST be able to list all active orders via `/orders`, with optional filtering by upcoming wedding date window (e.g., `/orders 30` for next 30 days).
- **FR-006**: Users MUST be able to update a dress's status via `/status <item_id> <new_status>`.
- **FR-013**: Users MUST be able to add a new dress record via `/add <model> <size> <cup_size> <location>`, with optional notes. Deletion of dress records is out of scope for the bot — it must be done via the web interface.
- **FR-007**: The bot MUST confirm every successful data change with a summary message showing the affected record.
- **FR-008**: The bot MUST provide clear error messages for invalid commands, unknown IDs, or invalid enum values (e.g., listing valid status options when an invalid one is provided).
- **FR-009**: Users MUST be able to retrieve the full command reference via `/help`.
- **FR-010**: The bot MUST respond to any unrecognized input with a prompt to use `/help`.
- **FR-011**: The bot MUST reflect the live state of the shared database; it reads from and writes to the same data store as the web interface.
- **FR-012**: Long responses (exceeding chat message limits) MUST be split into multiple sequential messages automatically.

### Bot Command Reference

| Command | Arguments | Description |
|---------|-----------|-------------|
| `/stock` | none | Show all dresses currently In Stock or Display |
| `/future` | none | Show dresses In Sewing, Abroad, or Out to Bride |
| `/dress` | `<model_number>` | Show all inventory records for a specific model |
| `/orders` | `[days]` (optional) | List active orders, optionally filtered by days until wedding |
| `/add` | `<model> <size> <cup> <location>` | Add a new dress record to inventory |
| `/status` | `<item_id> <new_status>` | Update a dress's status |
| `/help` | none | List all available commands |

### Key Entities

- **Dress** (`dress_inventory`): Individual physical dress. Attributes: item_id, model_number, size, cup_size (A/B/C/D), is_custom_sewing, storage_location (Tel Aviv/Ashdod/Abroad), dress_condition (Good/Laundry Damage/Replace Top/Replace Skirt), status (In Stock/Display/Abroad/In Sewing/Out to Bride), notes. May have linked orders.
- **Order** (`active_orders`): Bride's order. Attributes: order_id, model_number, bride_name, first_measurement_date, wedding_date, measurements (bust/hips/waist/height cm), cup_size, is_custom_sewing, order_type (Stock-based/New Order/Trunk-show), notes. Optionally linked to a specific dress via dress_id.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can retrieve live stock, future stock, or order information in under 10 seconds per query.
- **SC-002**: Every slash command either returns the correct result or an explanatory error — zero silent failures.
- **SC-003**: The bot's `/stock` and `/future` views always match the shared database state (no stale caching beyond 5 seconds).
- **SC-004**: The bot is available and responsive at least 99% of the time during business hours.
- **SC-005**: Users can identify a dress's availability and linked order details using only the bot, without needing to open the web interface.
- **SC-006**: The `/help` command is rated as clear and sufficient by all team members after first use.

## Assumptions

- The bot will serve a small pre-authorized team (the boutique staff); no public registration flow is needed.
- The bot integrates directly with the existing shared database used by the web interface; it does not maintain its own copy of inventory data.
- "Future stock" includes all out-of-boutique dresses (In Sewing, Abroad, Out to Bride, Trunk-show returns) AND New Order type orders representing custom dresses not yet physically received.
- The storage location "Abroad" on a dress (not an order) means the dress itself is physically overseas, distinct from being "Out to Bride."
- Natural language command support is explicitly deferred to a future version; v1 uses slash commands only.
- The bot will operate in a private Telegram group or direct chat limited to authorized staff.
- Trunk-show dresses may temporarily leave the boutique; their return tracking follows the same Out to Bride / Abroad flow.
