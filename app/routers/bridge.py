from fastapi import APIRouter, Header, Request, HTTPException
from app.security import verify_signature
from app.storage import insert_job, find_job_by_idemp
from app.models import IngestBody
from app.utils.logging import log

router = APIRouter()

@router.post("/ingest")
async def ingest(req: Request, x_signature: str | None = Header(default=None), idempotency_key: str | None = Header(default=None)):
    raw = await req.body()
    if not verify_signature(raw, x_signature):
        log("WARN", evt="ingest", ok=False, reason="unauthorized")
        raise HTTPException(status_code=401, detail="unauthorized")

    try:
        body = IngestBody.model_validate_json(raw)
    except Exception as e:
        log("WARN", evt="ingest", ok=False, reason="schema_error", err=str(e))
        raise HTTPException(status_code=422, detail="schema error")

    key = idempotency_key or body.idempotency_key
    if not key:
        log("WARN", evt="ingest", ok=False, reason="missing_idempotency_key")
        raise HTTPException(status_code=422, detail="missing idempotency_key")

    existing = find_job_by_idemp(key)
    if existing:
        log("INFO", evt="ingest", ok=True, dedup=True, id=existing, idemp=key)
        return {"ok": True, "queued": False, "dedup": True, "id": existing}

    jid = insert_job(key=key, body=body, hmac_hex=x_signature or "")
    log("INFO", evt="ingest", ok=True, dedup=False, id=jid, idemp=key)
    return {"ok": True, "queued": True, "id": jid}
