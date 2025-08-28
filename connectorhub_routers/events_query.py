from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from services.store import Store

router = APIRouter()

def _parse_time(s: Optional[str], default):
    if not s:
        return default
    try:
        return datetime.fromisoformat(s.replace("Z","+00:00"))
    except Exception:
        return default

@router.get("/query")
def query(
    source: Optional[str] = None,
    event: Optional[str] = None,
    trigger: Optional[str] = None,
    level: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    limit: int = Query(default=100, le=1000, ge=1),
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    since_dt = _parse_time(since, now - timedelta(hours=24))
    until_dt = _parse_time(until, now)

    store = Store()
    store.ensure_schema()
    rows = store.query_events(source=source, event=event, trigger=trigger, level=level,
                              since=since_dt, until=until_dt, limit=limit)
    return {"ok": True, "count": len(rows), "items": rows}
