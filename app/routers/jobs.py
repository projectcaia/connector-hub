from fastapi import APIRouter, Query
from app.storage import fetch_recent_jobs

router = APIRouter()

@router.get("/jobs")
def jobs(hours: int = Query(24, ge=1, le=168)):
    # default: last 24 hours; cap to 168h (7 days)
    items = fetch_recent_jobs(hours=hours)
    return {"ok": True, "items": items}
