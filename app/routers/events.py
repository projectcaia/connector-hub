from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from app.storage import recent_jobs

router = APIRouter()

@router.get("/events/recent")
def events_recent(limit: int = 3, x_signature: Optional[str] = Header(default=None, convert_underscores=True)):
    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    items = recent_jobs(limit=limit)
    return {"items": items}
