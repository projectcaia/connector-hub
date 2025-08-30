
from __future__ import annotations
from fastapi import APIRouter, Header, HTTPException, Request
from ..models import LegacyIngestRequest, HubExecuteRequest, HubParams, HubExecuteResponse
from .security import verify_bearer
from ..deps import get_db
import json

router = APIRouter(prefix="/bridge", tags=["bridge"])

def legacy_to_hub(req: LegacyIngestRequest) -> HubExecuteRequest:
    return HubExecuteRequest(
        service="agent",
        action="notify",
        params=HubParams(
            source=req.source,
            type=req.type,
            priority=req.priority,
            timestamp=req.timestamp,
            payload=req.payload,
        ),
        job_id=req.idempotency_key,
    )

@router.post("/ingest", response_model=HubExecuteResponse)
async def ingest(req: LegacyIngestRequest, authorization: str = Header(...)):
    # Auth
    verify_bearer(authorization)
    # Idempotency: ignore if same job already exists
    from ..storage_patch import find_job_by_idemp, upsert_job
    job = find_job_by_idemp(req.idempotency_key)
    if not job:
        upsert_job(
            idemp=req.idempotency_key,
            source=req.source,
            type_=req.type,
            priority=req.priority or "medium",
            timestamp=req.timestamp or "",
            payload_json=json.dumps(req.payload, ensure_ascii=False),
        )
    # Map to new schema and delegate to same storage path
    hub_req = legacy_to_hub(req)
    from ..deps import record_event
    eid = record_event(service=hub_req.service, action=hub_req.action, params=hub_req.params.model_dump(), job_id=hub_req.job_id)
    return {"ok": True, "event_id": eid, "job_id": hub_req.job_id}
