# Feature Specification: Shared Database Layer

**Feature Branch**: `002-shared-db-layer`
**Created**: 2026-04-16
**Status**: Draft
**Input**: User description: "create a better db module that (using sqlalchemy), the both bot and server can use, implement it as a senior backend engineer"

## Context

The system currently has two consumers of the inventory database — the FastAPI web server (`backend/`) and the Telegram bot (`bot/`) — but no shared, well-structured database layer. Database configuration, models, and query logic are scattered across several files, and the bot uses a path hack (`sys.path.insert`) to reach the backend's database code. This feature consolidates all database concerns into a single, professionally structured shared module.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single Source of Truth for Database Configuration (Priority: P1)

A developer working on either the API server or the Telegram bot opens one place to find the database engine configuration, session factory, and connection settings. There is no duplication — changing the database URL in one place changes it for both consumers.

**Why this priority**: Duplicate configuration is the root cause of environment-specific bugs and drift between server and bot behaviour. This is the foundational blocker for all other improvements.

**Independent Test**: Can be tested by verifying both the API server and the Telegram bot start and successfully connect to the database using only the shared module — no local database configuration files in either `backend/` or `bot/`.

**Acceptance Scenarios**:

1. **Given** the shared database module is installed, **When** the API server starts, **Then** it connects to the database using the configuration from the shared module without any local database setup.
2. **Given** the shared database module is installed, **When** the Telegram bot starts, **Then** it connects to the same database using the same shared configuration without path manipulation or local imports.
3. **Given** the database URL is changed in the shared module, **When** either consumer is restarted, **Then** both connect to the new database without any other code changes.

---

### User Story 2 - Safe Session Lifecycle Management (Priority: P1)

A developer writing a new query in either the server or the bot calls a single, well-defined function to obtain a database session. The session is always closed properly — whether the operation succeeds or raises an exception — with no risk of connection leaks.

**Why this priority**: Connection leaks cause silent degradation over time. A standardised session utility eliminates an entire class of bugs that are hard to reproduce and diagnose in production.

**Independent Test**: Can be tested by running a query that intentionally raises an exception mid-operation and confirming the session is released cleanly, with no open connection remaining.

**Acceptance Scenarios**:

1. **Given** a handler (API endpoint or bot command) obtains a session via the shared utility, **When** the operation completes successfully, **Then** the session is committed and closed automatically.
2. **Given** a handler obtains a session via the shared utility, **When** an exception occurs during the operation, **Then** the session is rolled back and closed without leaking the connection.
3. **Given** the API server uses dependency injection for sessions, **When** the shared session utility is used as the dependency provider, **Then** per-request session lifecycle is handled identically to the current behaviour, with no regression.

---

### User Story 3 - Consolidated Query Layer Accessible to Both Consumers (Priority: P2)

A developer implementing a new inventory feature writes a query function once in the shared module and calls it from both the API server and the Telegram bot. There is no duplication between `crud.py` and `bot_crud.py` — shared queries live in one place.

**Why this priority**: The current split between `crud.py` (server) and `bot_crud.py` (bot) means similar queries are written twice. Consolidation reduces maintenance burden and ensures the server and bot always operate on the same business logic.

**Independent Test**: Can be tested by replacing a duplicate query (e.g., fetching live stock) with a single shared implementation and verifying both the API endpoint and the bot `/stock` command return identical results.

**Acceptance Scenarios**:

1. **Given** a query function exists in the shared module, **When** the API server calls it, **Then** it returns the correct result without any server-specific adaptation.
2. **Given** the same query function exists in the shared module, **When** the Telegram bot calls it, **Then** it returns the correct result without any bot-specific adaptation or path workarounds.
3. **Given** a query needs to be updated (e.g., a new filter added), **When** it is changed in the shared module, **Then** both the server and bot immediately reflect the change with no additional modifications.

---

### User Story 4 - No Path Manipulation or Circular Import Risks (Priority: P2)

A developer adds a new file to the project and imports from the shared database module using a clean, standard import. There are no `sys.path.insert` calls, no relative path guessing, and no risk of import errors caused by running from an unexpected working directory.

**Why this priority**: The current `sys.path.insert` in `bot/utils/db.py` is a code smell that breaks in CI, packaging, and any non-standard working directory. It also signals that module boundaries are not properly defined.

**Independent Test**: Can be tested by running both the server and the bot from different working directories (e.g., project root, `backend/`, `bot/`) and confirming imports succeed in all cases without environment manipulation.

**Acceptance Scenarios**:

1. **Given** the shared module is properly structured, **When** any file in the project imports from it, **Then** the import uses a standard package path with no `sys.path` manipulation.
2. **Given** a developer runs the bot from the project root, **When** the bot starts, **Then** no import errors occur related to database module resolution.
3. **Given** a developer runs the API server from the `backend/` directory, **When** the server starts, **Then** no import errors occur related to database module resolution.

---

### User Story 5 - Environment-Based Configuration (Priority: P3)

A developer or deployment script sets the database URL via an environment variable. The shared module reads this variable and uses it for all connections. Switching between development, test, and production databases requires only changing the environment — no code changes.

**Why this priority**: Hardcoded database paths (`sqlite:///./inventory.db`) are a deployment anti-pattern. Environment-based configuration is a baseline senior-engineering practice that enables proper CI/CD and multi-environment operation.

**Independent Test**: Can be tested by setting `DATABASE_URL` to an in-memory SQLite database, starting either consumer, and confirming it connects to the in-memory database rather than the default file.

**Acceptance Scenarios**:

1. **Given** `DATABASE_URL` environment variable is set, **When** either consumer starts, **Then** the shared module connects to that database URL.
2. **Given** `DATABASE_URL` is not set, **When** either consumer starts, **Then** the shared module falls back to a documented default (`sqlite:///./inventory.db`) and logs a warning.
3. **Given** an invalid database URL is set, **When** either consumer starts, **Then** a clear, actionable error message is shown before the process exits.

---

### Edge Cases

- What happens when two processes (server and bot running simultaneously) both write to the same SQLite file at the same time?
- What happens when the database file does not exist at startup?
- What happens if a session is used after it has been closed?
- What happens when a migration runs while the bot or server has an active session?
- How are test suites isolated — do they use the same shared module with an overridden URL, or a separate fixture?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A shared database package MUST exist at the project root level, importable by both `backend/` and `bot/` without path manipulation.
- **FR-002**: The shared package MUST expose a single engine instance and session factory, configured from an environment variable with a documented fallback default.
- **FR-003**: The shared package MUST provide a session context manager that automatically commits on success and rolls back on exception, always closing the session.
- **FR-004**: The shared package MUST provide a FastAPI-compatible session dependency (generator function) that wraps the same session lifecycle logic, ensuring no regression in the API server.
- **FR-005**: All SQLAlchemy model definitions (DressInventory, ActiveOrder and their enums) MUST live exclusively in the shared package — no model definitions may remain in `backend/src/models.py` or any other non-shared location.
- **FR-006**: All query functions currently in `backend/src/crud.py` and `backend/src/bot_crud.py` MUST be consolidated into the shared package, with duplicates merged into single implementations.
- **FR-007**: The shared package MUST be importable as a proper Python package (with `__init__.py` exposing the public interface), not as a loose collection of files.
- **FR-008**: `backend/src/bot_crud.py` MUST be removed once its queries are migrated to the shared package.
- **FR-009**: `bot/utils/db.py` MUST be removed and replaced with a direct import from the shared package.
- **FR-010**: The shared package MUST configure SQLite with `check_same_thread=False` and appropriate connection pool settings for concurrent use by the async bot and sync server.
- **FR-011**: All existing API endpoints and bot commands MUST continue to function identically after the migration — zero functional regression.

### Key Entities

- **Shared DB Package**: A Python package at the project root providing engine, session factory, session utilities, models, and query functions to any consumer.
- **Session Context Manager**: A reusable utility that wraps a database session with automatic commit/rollback/close lifecycle, suitable for sync callers (bot's `asyncio.to_thread`) and direct server use.
- **FastAPI Session Dependency**: A generator-based session provider compatible with FastAPI's `Depends()` injection, wrapping the shared session lifecycle.
- **Query Module**: The consolidated set of all database query functions, replacing the current split between `crud.py` and `bot_crud.py`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero `sys.path` manipulation calls remain anywhere in the codebase after migration.
- **SC-002**: Database configuration appears in exactly one location — all other references are imports from that location.
- **SC-003**: All existing automated tests pass without modification after migration.
- **SC-004**: Both the API server and the Telegram bot start and operate correctly from the project root using only standard Python import syntax.
- **SC-005**: A new query function can be added in one place and called by both consumers without any additional wiring, in under 5 minutes.
- **SC-006**: Switching the database to an in-memory SQLite for testing requires changing only one environment variable — no code changes.

## Assumptions

- The project uses a single SQLite database file shared between the API server and the Telegram bot; multi-database or read-replica setups are out of scope.
- SQLite's file-level locking is acceptable for the current usage pattern (small team, low concurrency); no migration to PostgreSQL or another engine is in scope for this feature.
- The shared package will live at the project root as a first-class Python package (e.g., `db/` or `shared/`); the exact name is a planning-phase decision.
- Alembic migrations are out of scope for this feature; the existing `Base.metadata.create_all()` approach is retained.
- The shared package is not published to PyPI; it is used as a local package within the monorepo.
- Both `backend/src/crud.py` and `backend/src/bot_crud.py` are fully replaced by the shared query module; no partial migration is acceptable.
