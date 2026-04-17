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

- What happens if Supabase is temporarily unreachable? Both services should log the error to stderr and exit with a non-zero code; they must not silently corrupt data or fall back to SQLite in production.
- What if the Render worker (bot) restarts? Telegram's polling API retains messages for 24 hours; the bot will process any pending commands on resume. Missed commands during the restart window are acceptable for this internal tool.
- What if `DATABASE_URL` is missing from environment variables? The service logs a warning and falls back to SQLite (dev behaviour); in production this is prevented by Render's required env var configuration — no additional startup guard is required.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST connect to Supabase Postgres using a `DATABASE_URL` environment variable, with no hardcoded connection strings. The connection string format is `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`.
- **FR-002**: The FastAPI web service MUST serve both the REST API and the compiled React frontend static files from a single Render **web** service. The frontend is mounted at `/` with SPA fallback (`html=True`) so client-side routing works. All API routes take precedence over the static mount.
- **FR-003**: The Telegram bot MUST run as a separate Render **worker** service (not a web service) — worker services never sleep on Render's free tier.
- **FR-004**: Both services MUST use the shared `db/` SQLAlchemy layer for all database access. SQLAlchemy's `Base.metadata.create_all()` runs at startup and creates all tables on first deploy — no separate migration step is needed.
- **FR-005**: The SQLite-specific `connect_args={"check_same_thread": False}` MUST be made conditional (applied only when `DATABASE_URL` starts with `sqlite`) so Postgres connections function correctly.
- **FR-006**: Deployments MUST be triggered automatically when the `main` branch is updated, via Render's GitHub integration declared in `render.yaml`.
- **FR-007**: All secrets (`DATABASE_URL`, Telegram bot token) MUST be stored as Render environment variables (declared `sync: false` in `render.yaml`), never in committed files or build logs. The web service receives `DATABASE_URL` only; the worker receives both `DATABASE_URL` and `TELEGRAM_BOT_TOKEN`.
- **FR-008**: The React frontend build artifact (`frontend/dist/`) MUST be produced at build time (`npm run build`) and served as static files by FastAPI in production.
- **FR-009**: CORS `allow_origins` MUST be restricted to the Render web service's own origin in production (same-origin requests from the served frontend require no CORS headers). `allow_origins=["*"]` is only acceptable in local development.

### Key Entities

- **Render Web Service**: Hosts FastAPI backend + compiled React frontend. Auto-deploys from GitHub. Acceptable cold start for internal use.
- **Render Worker**: Hosts Telegram bot with polling. Never sleeps. Auto-deploys from GitHub.
- **Supabase Project**: Managed Postgres database. Single source of truth shared by both services.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The web app is accessible via a public URL within 30 seconds of a cold start (maximum acceptable cold start time).
- **SC-002**: The Telegram bot responds to commands within 5 seconds under normal conditions. This is a best-effort guideline for the Render free tier; occasional higher latency is acceptable for an internal tool.
- **SC-003**: A change made via the web app is visible via the bot (and vice versa) within 2 seconds. This is a best-effort target reflecting direct Postgres writes with no caching layer — not a hard SLA.
- **SC-004**: Zero manual steps required for routine deploys and service restarts (git push to `main` triggers both). Secret rotation and database backups are explicitly out of scope for this phase.
- **SC-005**: All infrastructure runs within free tier limits of Render and Supabase. If free tier limits (Supabase 500 MB storage, Render monthly credit) are approached, the team will be notified via Render/Supabase dashboards — no automated alerting is required for this internal tool.

## Assumptions

- The app is for a small internal team; cold start delays (up to 30s) on the free web service tier are acceptable.
- Existing SQLAlchemy models are fully Postgres-compatible (no SQLite-specific column types used). This is validated by T003/T007 in tasks.md before deploy.
- The React frontend is a standard Vite SPA that produces a `frontend/dist/` build output folder.
- The web UI is publicly accessible via the Render URL (no IP restriction or authentication required). This is an explicit decision for this internal tool phase.
- Existing inventory data in SQLite does not need to be migrated; a fresh start on Supabase is acceptable. **This assumption must be confirmed by all team members before deploy.**
- The Telegram bot uses polling (not webhooks), so it requires an always-on Render worker process.
- Supabase's built-in daily backups (retained 7 days on the free tier) are sufficient for disaster recovery for this internal tool.
- Concurrent writes from the web app and bot are handled by Postgres row-level locking; no application-level concurrency control is required at this scale.
- Secret rotation (DB password, bot token) is a manual process done via the Render and Supabase dashboards when needed; no automated rotation is required for this phase.
- Render automatically retains the previous successful deployment and allows one-click rollback via its dashboard if a new deploy fails.
