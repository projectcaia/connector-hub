from fastapi import APIRouter
from services.store import Store

router = APIRouter()

@router.get("/ready")
def ready():
    return {"ok": True, "service": "connectorhub-ext", "version": "2025.08.28"}

@router.get("/health")
def health():
    try:
        Store().ensure_schema()
        return {"ok": True, "db": "ok"}
    except Exception as e:
        return {"ok": False, "db": str(e)}
