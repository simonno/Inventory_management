# Feature Specification: Deploy to Render + Supabase

**Feature Branch**: `003-render-supabase-deploy`  
**Created**: 2026-04-17  
**Status**: Draft  
**Input**: User description: "Deploy app (FastAPI + React frontend + Telegram bot) to Render with Supabase Postgres, replacing SQLite, with minimal infrastructure maintenance"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - App is live and accessible (Priority: P1)

A team member opens the inventory web app from any browser and can view, add, and update inventory items. The app is deployed to a stable URL with no local setup required.

**Why this priority**: This is the core deliverable — the app must be reachable without running it locally.

**Independent Test**: Navigate to the Render web service URL and perform a full CRUD operation on an inventory item.

**Acceptance Scenarios**:

1. **Given** the Render web service is deployed, **When** a user visits the public URL, **Then** the React inventory UI loads successfully.
2. **Given** the UI is loaded, **When** a user adds or updates an inventory item, **Then** the change is persisted and visible on refresh.

---

### User Story 2 - Telegram bot responds to commands (Priority: P2)

A team member sends a slash command to the Telegram bot and receives an accurate response reflecting the current inventory state — reading from and writing to the same database as the web app.

**Why this priority**: The bot is the second primary interface; it must be always-on and share real-time data with the web app.

**Independent Test**: Send a list command to the bot and verify it returns current inventory data that matches the web app.

**Acceptance Scenarios**:

1. **Given** the Render worker is deployed, **When** a user sends a bot command, **Then** the bot responds within 5 seconds.
2. **Given** a user adds an item via the web app, **When** the bot is queried, **Then** the bot reflects the newly added item.

---

### User Story 3 - Database migration from SQLite to Supabase (Priority: P1)

All inventory data is stored in Supabase Postgres. Both the web app and Telegram bot connect exclusively to Supabase. No SQLite file is used in production.

**Why this priority**: Without this, both services cannot share a single source of truth in the cloud.

**Independent Test**: Deploy with `DATABASE_URL` pointing to Supabase. Create a record via web app, query it via bot — both must reflect the same data.

**Acceptance Scenarios**:

1. **Given** `DATABASE_URL` is set to Supabase in Render environment variables, **When** the web service starts, **Then** it connects to Supabase without errors.
2. **Given** both services use the same `DATABASE_URL`, **When** data is written by one service, **Then** it is immediately readable by the other.

---

### Edge Cases

- What happens if Supabase is temporarily unreachable? Both services should fail gracefully with a clear error, not silently corrupt data.
- What if the Render worker (bot) restarts? It should resume polling without data loss.
- What if `DATABASE_URL` is missing from environment variables? Services should fail at startup with a clear configuration error, not at runtime.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST connect to Supabase Postgres using a `DATABASE_URL` environment variable, with no hardcoded connection strings.
- **FR-002**: The FastAPI web service MUST serve both the REST API and the compiled React frontend static files from a single Render web service.
- **FR-003**: The Telegram bot MUST run as a separate Render worker service (always-on, no sleep).
- **FR-004**: Both services MUST use the shared `db/` SQLAlchemy layer for all database access.
- **FR-005**: The SQLite-specific connection argument MUST be removed or made conditional so Postgres connections function correctly.
- **FR-006**: Deployments MUST be triggered automatically from the main Git branch via Render's GitHub integration.
- **FR-007**: All secrets (`DATABASE_URL`, Telegram bot token) MUST be stored as Render environment variables, never in code or committed files.
- **FR-008**: The React frontend build artifact MUST be served as static files by FastAPI in production.

### Key Entities

- **Render Web Service**: Hosts FastAPI backend + compiled React frontend. Auto-deploys from GitHub. Acceptable cold start for internal use.
- **Render Worker**: Hosts Telegram bot with polling. Never sleeps. Auto-deploys from GitHub.
- **Supabase Project**: Managed Postgres database. Single source of truth shared by both services.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The web app is accessible via a public URL within 30 seconds of a cold start.
- **SC-002**: The Telegram bot responds to commands within 5 seconds under normal conditions.
- **SC-003**: A change made via the web app is visible via the bot (and vice versa) within 2 seconds.
- **SC-004**: Zero manual server maintenance steps are required for routine operation (deploys, restarts).
- **SC-005**: All infrastructure runs within free tier limits of Render and Supabase.

## Assumptions

- The app is for a small internal team; cold start delays on the free web service tier are acceptable.
- Existing SQLAlchemy models are fully Postgres-compatible (no SQLite-specific column types used).
- The React frontend is a standard Vite SPA that produces a static build output folder.
- No user authentication layer is required for this deployment phase.
- Existing inventory data in SQLite does not need to be migrated; a fresh start on Supabase is acceptable.
- The Telegram bot uses polling (not webhooks), so it requires an always-on process.
