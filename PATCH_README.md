
# ConnectorHub Dual-Layout AutoPatch (2025-08-30)
Fixes: sqlite3.OperationalError: no column named job_id on table events

## What this does
- Ensures /data/hub.db is used (set DB_PATH env)
- Creates 'events' table if missing
- Adds 'job_id' column if missing
- Works whether your app imports 'deps' from project root or from /app

## Files in this zip
- deps.py
- connectorhub_db_patch.py
- app/deps.py  (mirror)
- app/connectorhub_db_patch.py  (mirror)

## How to apply
1) Set env: DB_PATH=/data/hub.db
2) Unzip into your repo root (overwrite existing files)
3) Redeploy / restart
4) Check logs for:
   - [PATCH] Added missing column: job_id to events (first run)
   - [PATCH] DB schema ensured successfully at /data/hub.db
