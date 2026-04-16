# Tasks: Telegram Inventory Bot

**Input**: Design documents from `/specs/001-telegram-inventory-bot/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/bot-commands.md ✅ quickstart.md ✅

**Tests**: Not requested in feature spec — no test tasks included. Unit test stubs noted in Polish phase.

**Organization**: Tasks grouped by user story for independent implementation and delivery.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US6)
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the `bot/` module structure and install dependencies. No existing code is modified.

- [x] T001 Create directory structure: `bot/`, `bot/handlers/`, `bot/utils/` with `__init__.py` files in each
- [x] T002 Create `bot-requirements.txt` at repo root with content: `python-telegram-bot==20.*`
- [x] T003 [P] Create empty `bot/main.py` with module docstring placeholder
- [x] T004 [P] Create empty `backend/src/bot_crud.py` with module docstring placeholder

**Checkpoint**: Directory tree matches `quickstart.md` project structure. `bot-requirements.txt` exists.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Data layer and shared utilities that ALL command handlers depend on. Must be complete before any user story handler can be built.

**⚠️ CRITICAL**: No handler work can begin until this phase is complete.

### Data layer

- [x] T005 Implement `get_live_stock(db)` in `backend/src/bot_crud.py` — query dresses with status In Stock or Display, ordered by model_number ASC, size ASC. Returns `List[DressInventory]`.
- [x] T006 Implement `get_future_stock(db)` in `backend/src/bot_crud.py` — query dresses with status In Sewing, Abroad, or Out to Bride (joined with linked orders for wedding dates); also query orders with order_type New Order. Returns `dict` with keys `"dresses"` (List[DressInventory]) and `"new_orders"` (List[ActiveOrder]).
- [x] T007 [P] Implement `get_dresses_by_model(db, model_number)` in `backend/src/bot_crud.py` — case-insensitive filter on model_number, eagerly loads linked orders, ordered by size ASC, cup_size ASC. Returns `List[DressInventory]`.
- [x] T008 [P] Implement `get_orders_filtered(db, days=None)` in `backend/src/bot_crud.py` — if days provided filter wedding_date BETWEEN today AND today+days, else return all; ordered by wedding_date ASC. Returns `List[ActiveOrder]`.
- [x] T009 [P] Implement `update_dress_status(db, item_id, new_status)` in `backend/src/bot_crud.py` — fetch by item_id (return None if not found), validate new_status is valid DressStatus enum value, update and commit. Returns updated `DressInventory` or None.
- [x] T010 [P] Implement `add_dress(db, model_number, size, cup_size, location, condition='Good', notes=None)` in `backend/src/bot_crud.py` — validate enum values for cup_size, location, condition; create with status=In Stock; return created `DressInventory`.

### Bot utilities

- [x] T011 Implement `get_db_session()` context manager in `bot/utils/db.py` — wraps the existing `backend/src/database.SessionLocal` in a try/finally that closes the session. Suitable for use inside `asyncio.to_thread()` calls in async handlers.
- [x] T012 Implement `split_message(text, limit=4096)` in `bot/utils/formatting.py` — splits text at newline boundaries so no chunk exceeds `limit` characters. Returns `List[str]`. Used by all handlers for long responses.
- [x] T013 [P] Implement `format_condition_flag(condition)` helper in `bot/utils/formatting.py` — returns `" ⚠️"` if condition is not "Good", else empty string. Used by stock formatters.

**Checkpoint**: All `bot_crud` functions importable and working. `db.py` and `formatting.py` utilities ready. Handlers can now be built.

---

## Phase 3: User Story 6 — `/help` Command (Priority: P1) 🎯 Bot Validation

**Goal**: A working, registered bot that responds to `/help` and unknown messages. Validates the full bot skeleton end-to-end before any inventory logic is added.

**Independent Test**: Start the bot (`python -m bot.main`), send `/help` to the bot in Telegram, and verify it lists all 7 commands with descriptions. Send any unknown text and verify the fallback message appears.

- [x] T014 [US6] Implement `/help` handler in `bot/handlers/help.py` — respond with the formatted command list from `contracts/bot-commands.md`; include all 7 commands with one-line descriptions.
- [x] T015 [US6] Implement unknown message fallback in `bot/handlers/help.py` — `MessageHandler` that responds "Unknown command. Send /help to see available commands." for any non-command text.
- [x] T016 [US6] Implement `bot/main.py` — load `TELEGRAM_BOT_TOKEN` from environment variable (raise clear error if missing); register `CommandHandler("help", ...)` and the unknown message `MessageHandler`; start polling loop.

**Checkpoint**: Bot starts, `/help` returns the command list, unknown input returns the fallback message. Bot framework validated.

---

## Phase 4: User Story 1 — `/stock` Live Stock View (Priority: P1) 🎯 MVP

**Goal**: Users can send `/stock` and receive all currently available dresses grouped by model number.

**Independent Test**: Send `/stock` to the bot. Verify response lists only dresses with status In Stock or Display, grouped by model number with size/cup/location/condition per line. Send `/stock` when inventory is empty and verify the empty-state message appears.

- [x] T017 [US1] Implement `format_live_stock(dresses)` in `bot/utils/formatting.py` — groups `List[DressInventory]` by model_number, formats each dress as a sub-item line showing size, cup size, location, condition (with `⚠️` flag if not Good), adds total count footer.
- [x] T018 [US1] Implement `/stock` handler in `bot/handlers/stock.py` — call `get_live_stock` via `asyncio.to_thread`, format result with `format_live_stock`, split with `split_message`, send all chunks. Handle DB failure with a user-friendly error message.
- [x] T019 [US1] Register `CommandHandler("stock", ...)` in `bot/main.py`.

**Checkpoint**: `/stock` returns correctly grouped live inventory. Empty state handled. DB errors show a friendly message.

---

## Phase 5: User Story 2 — `/future` Future Stock View (Priority: P1)

**Goal**: Users can send `/future` and see all out-of-boutique dresses and pending new orders grouped by category with expected return dates where available.

**Independent Test**: Send `/future` to the bot. Verify response groups dresses under In Sewing / Abroad / Out to Bride headings, shows wedding date for Out to Bride dresses, lists New Order orders separately. Verify empty state when nothing is out.

- [x] T020 [US2] Implement `format_future_stock(result)` in `bot/utils/formatting.py` — takes `dict` with `"dresses"` and `"new_orders"`; groups dresses by status (In Sewing → Out to Bride → Abroad); for Out to Bride dresses with a linked order, shows bride name and wedding date as expected return; appends New Orders section. Adds summary footer.
- [x] T021 [US2] Implement `/future` handler in `bot/handlers/future.py` — call `get_future_stock` via `asyncio.to_thread`, format with `format_future_stock`, split and send. Handle DB failure gracefully.
- [x] T022 [US2] Register `CommandHandler("future", ...)` in `bot/main.py`.

**Checkpoint**: `/future` correctly separates physical out-of-house dresses from new orders, shows return dates, handles empty state.

---

## Phase 6: User Story 3 — `/dress` Model Lookup (Priority: P2)

**Goal**: Users can send `/dress <model_number>` and see all inventory records for that model with linked order info.

**Independent Test**: Send `/dress <known_model>` — verify all dress records for that model appear with status, location, condition, and linked order details. Send `/dress <unknown_model>` — verify "not found" message. Send `/dress` with no argument — verify usage hint appears.

- [x] T023 [US3] Implement `format_dress_detail(dresses)` in `bot/utils/formatting.py` — lists each dress with item_id, size, cup size, location, status, condition; if dress has a linked order, shows bride name and wedding date indented below. Adds total count footer.
- [x] T024 [US3] Implement `/dress` handler in `bot/handlers/dress.py` — parse model_number argument (show usage hint if missing); call `get_dresses_by_model` via `asyncio.to_thread`; if empty return "not found" message; else format and send. Handle DB failure gracefully.
- [x] T025 [US3] Register `CommandHandler("dress", ...)` in `bot/main.py`.

**Checkpoint**: `/dress <model>` returns full detail for all matching records. Missing argument and unknown model handled correctly.

---

## Phase 7: User Story 4 — `/orders` Active Orders List (Priority: P2)

**Goal**: Users can send `/orders` or `/orders <days>` and see active orders sorted by wedding date.

**Independent Test**: Send `/orders` — verify all orders shown sorted by wedding_date. Send `/orders 30` — verify only orders within 30 days shown. Send `/orders abc` — verify invalid input error. Send `/orders` with no orders — verify empty state message.

- [x] T026 [US4] Implement `format_orders(orders, days=None)` in `bot/utils/formatting.py` — formats each order as a numbered line with bride name, model, size, cup, order type, and wedding date. Includes filter description in header ("next 30 days" or "all orders"). Adds total count footer.
- [x] T027 [US4] Implement `/orders` handler in `bot/handlers/orders.py` — parse optional `days` integer argument (return error if non-integer provided); call `get_orders_filtered` via `asyncio.to_thread`; format and send. Handle DB failure gracefully.
- [x] T028 [US4] Register `CommandHandler("orders", ...)` in `bot/main.py`.

**Checkpoint**: `/orders` and `/orders 30` both work. Invalid days value returns a clear error. Empty state handled.

---

## Phase 8: User Story 5 — `/status` Update Dress Status (Priority: P2)

**Goal**: Users can update a dress's status by item_id via `/status <item_id> <new_status>`. Bot confirms the change or explains what went wrong.

**Independent Test**: Send `/status <valid_id> in sewing` — verify status updated and confirmation shows old→new status. Send `/status <valid_id> badstatus` — verify error listing valid options. Send `/status 9999 in stock` — verify "not found" message. Send `/status` with missing args — verify usage hint.

- [x] T029 [US5] Implement `format_status_update(old_dress, updated_dress)` in `bot/utils/formatting.py` — shows dress id, model, size, cup, old status → new status, location.
- [x] T030 [US5] Implement `/status` handler in `bot/handlers/status.py` — parse item_id (integer) and new_status (join remaining args to support multi-word statuses like "in sewing"); show usage hint if either arg missing; call `update_dress_status` via `asyncio.to_thread`; if None returned show "not found"; if invalid status enum show valid options list; else show confirmation. Handle DB failure gracefully.
- [x] T031 [US5] Register `CommandHandler("status", ...)` in `bot/main.py`.

**Checkpoint**: Status updates work end-to-end. Invalid item IDs, invalid statuses, and missing args all handled with specific error messages.

---

## Phase 9: `/add` Command — Add New Dress (FR-013)

**Goal**: Users can add a new dress to inventory via `/add <model> <size> <cup> <location>`. Default status is In Stock, default condition is Good.

**Independent Test**: Send `/add 1234 38 B "tel aviv"` — verify dress appears in `/stock` afterwards with correct attributes. Send with invalid cup or location — verify specific enum error. Send with missing args — verify usage hint.

- [x] T032 [P] Implement `format_dress_added(dress)` in `bot/utils/formatting.py` — shows new item_id, model, size, cup, status, location, condition.
- [x] T033 Implement `/add` handler in `bot/handlers/add.py` — parse exactly 4 positional arguments (model, size, cup, location; quoted strings supported via Telegram message splitting); show usage hint if wrong count; validate cup_size and location against enum values (case-insensitive, show valid options on error); call `add_dress` via `asyncio.to_thread`; show confirmation with new item_id. Handle DB failure gracefully.
- [x] T034 Register `CommandHandler("add", ...)` in `bot/main.py`.

**Checkpoint**: `/add` creates a new dress and it immediately appears in `/stock`. Enum validation errors are specific and helpful.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, consistency, and documentation across all commands.

- [x] T035 [P] Review all handlers for consistent error message tone and format — ensure every error states what went wrong, shows usage syntax, and gives a concrete example (per `contracts/bot-commands.md` error contract)
- [x] T036 [P] Add `TELEGRAM_BOT_TOKEN` missing-token guard in `bot/main.py` — print clear setup instructions and exit if env var not set
- [x] T037 [P] Create `bot/tests/test_bot_crud.py` stub — placeholder test file with one passing smoke test per `bot_crud` function (using in-memory SQLite); enables future TDD
- [x] T038 [P] Create `bot/tests/test_handlers.py` stub — placeholder tests for argument parsing logic in each handler (no Telegram API calls)
- [x] T039 Register bot commands with BotFather — send `/setcommands` using the exact text from `contracts/bot-commands.md` BotFather section
- [x] T040 Verify `quickstart.md` setup steps produce a working bot end-to-end (manual walkthrough of all 7 commands)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **blocks all handler phases**
- **Phase 3 (US6 /help)**: Depends on Phase 2 — validates bot skeleton
- **Phase 4–9 (US1–US5 + /add)**: Depend on Phase 2; can proceed in any order after Phase 3 (bot skeleton validated)
- **Phase 10 (Polish)**: Depends on Phases 3–9

### User Story Dependencies

| Story | Command | Priority | Depends On |
|-------|---------|----------|------------|
| US6 | /help | P1 | Phase 2 |
| US1 | /stock | P1 | Phase 2 + T017 (formatter) |
| US2 | /future | P1 | Phase 2 + T020 (formatter) |
| US3 | /dress | P2 | Phase 2 + T023 (formatter) |
| US4 | /orders | P2 | Phase 2 + T026 (formatter) |
| US5 | /status | P2 | Phase 2 + T029 (formatter) |
| —   | /add   | FR | Phase 2 + T032 (formatter) |

All P1 stories (US6, US1, US2) are independent of each other after Phase 2.
All P2 stories (US3, US4, US5) are independent of each other after Phase 2.

### Within Each User Story

- Formatter task → handler task → registration task (sequential within story)
- All formatter tasks for different stories are parallelizable

### Parallel Opportunities

| Parallel Group | Tasks |
|----------------|-------|
| Phase 2 data layer | T005, T006, T007, T008, T009, T010 (after T004) |
| Phase 2 utilities | T011, T012, T013 (independent of data layer tasks) |
| P1 story formatters | T017 (/stock), T020 (/future) — after T013 |
| P2 story formatters | T023 (/dress), T026 (/orders), T029 (/status) — after T013 |
| Phase 10 polish | T035, T036, T037, T038 |

---

## Parallel Example: Phase 2 Foundational

```bash
# Run these data layer tasks in parallel (all write to bot_crud.py but different functions):
T007: get_dresses_by_model
T008: get_orders_filtered
T009: update_dress_status
T010: add_dress

# Run these utility tasks in parallel with the data layer:
T011: bot/utils/db.py
T012: bot/utils/formatting.py (split_message)
T013: bot/utils/formatting.py (format_condition_flag)
```

## Parallel Example: P1 Stories After Phase 3

```bash
# After /help (Phase 3) validates the bot works:
T017→T018→T019: /stock handler
T020→T021→T022: /future handler
# These can proceed concurrently
```

---

## Implementation Strategy

### MVP First (Bot Validated + Live Stock)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (data layer + utilities)
3. Complete Phase 3: `/help` — validates full bot skeleton
4. Complete Phase 4: `/stock` — delivers first inventory query
5. **STOP and VALIDATE**: Bot live, team can check inventory via Telegram
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Framework ready
2. `/help` → Bot running end-to-end (Phase 3) 🎉
3. `/stock` → Live inventory visible (Phase 4) 🎉 MVP
4. `/future` → Future stock visible (Phase 5) 🎉
5. `/dress`, `/orders`, `/status` → Full read + status management (Phases 6–8)
6. `/add` → New dress creation from Telegram (Phase 9)
7. Polish → Production-ready (Phase 10)

---

## Notes

- [P] tasks operate on different files or independent functions — safe to run in parallel
- [Story] label maps each task to its user story for traceability
- `bot_crud.py` functions (T005–T010) may be implemented in parallel since they are separate functions in one file; coordinate to avoid merge conflicts if pair programming
- Always test commands in Telegram after completing each phase checkpoint
- No existing backend files are modified except adding `backend/src/bot_crud.py`
- Commit after each phase checkpoint at minimum
