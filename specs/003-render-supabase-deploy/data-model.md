# Data Model: Deploy to Render + Supabase

No new entities introduced by this feature. The existing SQLAlchemy models in `db/models.py` are used unchanged. Supabase Postgres is schema-compatible with the existing SQLite schema — SQLAlchemy's `Base.metadata.create_all()` will create all tables on first startup.

## Existing Entities (unchanged)

- **DressInventory**: Dress items with size, color, condition, storage location, status
- **ActiveOrder**: Orders linked to dresses, with customer details and order type
- **Enums**: CupSize, OrderType, StorageLocation, DressCondition, DressStatus

## Environment Variables (new)

| Variable | Service | Description |
|---|---|---|
| `DATABASE_URL` | web + worker | Supabase Postgres connection string (`postgresql://...`) |
| `TELEGRAM_BOT_TOKEN` | worker only | Telegram bot token from BotFather |
