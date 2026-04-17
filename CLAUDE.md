# Inventory_management Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-17

## Active Technologies
- Python 3.9 (existing venv) + SQLAlchemy (existing), Pydantic (existing) — no new dependencies required (002-shared-db-layer)
- SQLite (`inventory.db`) — unchanged; `NullPool` added for thread safety (002-shared-db-layer)
- Python 3.9, Node 18+ + FastAPI, SQLAlchemy, python-telegram-bot==20.*, psycopg2-binary (new), Vite (003-render-supabase-deploy)
- Supabase Postgres (replaces SQLite in production) (003-render-supabase-deploy)

- Python 3.9 (matches existing backend venv) + `python-telegram-bot==20.*`, SQLAlchemy (existing), Pydantic (existing) (001-telegram-inventory-bot)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.9 (matches existing backend venv): Follow standard conventions

## Recent Changes
- 003-render-supabase-deploy: Added Python 3.9, Node 18+ + FastAPI, SQLAlchemy, python-telegram-bot==20.*, psycopg2-binary (new), Vite
- 002-shared-db-layer: Added Python 3.9 (existing venv) + SQLAlchemy (existing), Pydantic (existing) — no new dependencies required

- 001-telegram-inventory-bot: Added Python 3.9 (matches existing backend venv) + `python-telegram-bot==20.*`, SQLAlchemy (existing), Pydantic (existing)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
