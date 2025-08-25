from fastapi import APIRouter
from datetime import datetime, timezone
from app.deps import get_db

router = APIRouter()

@router.get("/ready")
def ready():
    return {"ok": True, "version": "2025.08.25", "ts": datetime.now(timezone.utc).isoformat()}

@router.get("/health")
def health():
    with get_db() as conn:
        conn.execute("SELECT 1")
    return {"ok": True}
