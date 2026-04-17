# Quickstart: Deploy to Render + Supabase

## Prerequisites

- Supabase account (free): https://supabase.com
- Render account (free): https://render.com
- Repo connected to GitHub

## 1. Create Supabase Project

1. Create new project in Supabase dashboard
2. Go to **Settings → Database → Connection string → URI**
3. Copy the connection string (looks like `postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres`)

## 2. Deploy to Render

1. Push this branch to GitHub (merge to main)
2. In Render dashboard → **New → Blueprint** → connect repo
3. Render detects `render.yaml` and creates both services automatically
4. Set environment variables for each service:
   - Both services: `DATABASE_URL` = Supabase URI from step 1
   - Worker only: `TELEGRAM_BOT_TOKEN` = your bot token

## 3. Verify

- Web service URL (from Render dashboard) → opens inventory UI
- Telegram bot → send `/stock` → returns inventory from Supabase
- Add item in web UI → query via bot → same data appears

## Local Development (unchanged)

```bash
# Backend (SQLite fallback still works)
cd backend && uvicorn src.main:app --reload

# Bot
TELEGRAM_BOT_TOKEN=xxx python -m bot.main

# Frontend
cd frontend && npm run dev
```
