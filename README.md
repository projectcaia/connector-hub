# ConnectorHub Extension (v2025.08.28)

**Purpose**: Add `/hub/execute` broadcast flow + `/events/query` filtering without breaking your existing hub.
Runs side-by-side on port **8081** by default, or merge routers into the existing app if preferred.

## What’s new
- `POST /hub/execute`: Receive events from external agents (n8n, Zapier, Jenspark…)
- `GET /events/query`: Filter & retrieve stored events (by source, trigger, level, time range)
- Optional Telegram push + optional forward to "ConnectorGPT" summarizer
- SQLite WAL store (`/data/connectorhub_events.db`) — zero external deps

## Run (Docker)
```bash
docker build -t connectorhub-ext:20250828 .
docker run --rm -it -p 8081:8081 \  -e CONNECTOR_SECRET=your_token \  -e DB_PATH=/data/connectorhub_events.db \  -e PORT=8081 \  -v $(pwd)/data:/data connectorhub-ext:20250828
# open http://localhost:8081/ready
```

## API
### POST /hub/execute
**Headers**
- `Authorization: Bearer <CONNECTOR_SECRET>`
- `Content-Type: application/json`

**Body**
```jsonc
{
  "service": "agent" | "mail" | "memory" | "github",
  "action": "notify" | "read" | "write" | "recall",
  "params": {
    "source": "n8n" | "zapier" | "jenspark" | "...",
    "event": "센티넬 알람",
    "summary": "ΔK200 -1.8%, Reflex LV2 조건 충족",
    "trigger": "Reflex",
    "level": "LV2",
    "meta": { "any": "json" }
  }
}
```

**Response**
```json
{
  "ok": true,
  "id": "evt_20250828_120000_abc123",
  "stored": true,
  "broadcast": {"telegram": false, "connector_gpt": false},
  "ersp": {
    "event": "...",
    "interpretation": "...",
    "lesson": "...",
    "if_then": "..."
  }
}
```

### GET /events/query
Query params: `source, event, trigger, level, since, until, limit=100`
- Times are ISO8601, default since = now - 24h

### GET /ready
Liveness/version info.

### GET /health
DB connectivity.

## Merge into existing hub (optional)
If you want a single process instead of sidecar:
```python
# in your existing FastAPI app factory
from connectorhub_routers import hub, events_query
app.include_router(hub.router, prefix="/hub")
app.include_router(events_query.router, prefix="/events")
```
Make sure to set `DB_PATH` to point at your existing data mount.

---
© FGPT / Caia – ConnectorHub extension 2025-08-28
