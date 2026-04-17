# Research: Deploy to Render + Supabase

## Decision 1: Database driver for Postgres
- **Decision**: `psycopg2-binary`
- **Rationale**: SQLAlchemy's standard sync Postgres driver; `psycopg2-binary` is self-contained (no system libpq needed), suitable for Render's managed build environment
- **Alternatives considered**: `asyncpg` (async only, would require rewriting all sync SQLAlchemy code), `pg8000` (pure Python but slower)

## Decision 2: Fix `connect_args` in db/engine.py
- **Decision**: Make `connect_args={"check_same_thread": False}` conditional on SQLite
- **Rationale**: This argument is SQLite-specific; passing it to a Postgres connection raises `TypeError`. The fix is one line: check if URL starts with `sqlite`.
- **Alternatives considered**: Remove entirely (breaks existing SQLite dev workflow)

## Decision 3: Frontend static file serving
- **Decision**: Mount `frontend/dist` as StaticFiles in FastAPI at `"/"`, remove the `GET /` JSON route
- **Rationale**: Single Render web service serves both API and SPA. StaticFiles with `html=True` handles SPA client-side routing. API routes registered before the mount take precedence.
- **Alternatives considered**: Separate Vercel for frontend (more services, more maintenance), Nginx sidecar (overkill for free tier)

## Decision 4: Single root requirements.txt
- **Decision**: Create `requirements.txt` at repo root combining backend + bot dependencies, adding `psycopg2-binary`, removing `aiosqlite`
- **Rationale**: Both Render services (web + worker) share one repo. A single file simplifies build commands. `aiosqlite` is SQLite async driver — not needed for Postgres.
- **Alternatives considered**: Separate requirements per service (more config, more drift risk)

## Decision 5: render.yaml for IaC deployment
- **Decision**: Use `render.yaml` (Render Blueprint) at repo root
- **Rationale**: Declarative config in version control means zero manual dashboard clicks for new deployments. Auto-deploy on push to main.
- **Alternatives considered**: Manual Render dashboard setup (not reproducible, easy to misconfigure)

## Decision 6: Bot run mode
- **Decision**: Polling (keep existing `app.run_polling()`)
- **Rationale**: Render worker services are long-running processes — polling fits naturally. Webhooks would require a public HTTPS endpoint and more Render config.
- **Alternatives considered**: Webhooks (more complex, no benefit at this scale)
