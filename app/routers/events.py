
from __future__ import annotations
from fastapi import APIRouter, Header, Query
from ..deps import list_events
from .security import verify_bearer

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/query")
async def query_events(limit: int = Query(10, ge=1, le=100), authorization: str = Header(...)):
    verify_bearer(authorization)
    return {"ok": True, "items": list_events(limit)}
