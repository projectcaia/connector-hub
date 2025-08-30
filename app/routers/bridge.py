
from __future__ import annotations
from fastapi import APIRouter, Header
from ..models import LegacyIngestRequest, HubExecuteRequest, HubParams, HubExecuteResponse
from ..deps import record_event
from .security import verify_bearer
from ..storage_patch import find_job_by_idemp, upsert_job
import json

router = APIRouter(prefix="/bridge", tags=["bridge"])

def legacy_to_hub(req: LegacyIngestRequest) -> HubExecuteRequest:
    # Map legacy fields to new schema, derive 'event' from payload.note or type
    event = req.payload.get("note") or req.type
    return HubExecuteRequest(
        service="agent",
        action="notify",
        params=HubParams(
            source=req.source,
            type=req.type,
            event=event,
            priority=req.priority,
            timestamp=req.timestamp,
            payload=req.payload,
        ),
        job_id=req.idempotency_key,
    )

@router.post("/ingest", response_model=HubExecuteResponse)
async def ingest(req: LegacyIngestRequest, authorization: str = Header(...)):
    verify_bearer(authorization)
    # idempotency
    if not find_job_by_idemp(req.idempotency_key):
        upsert_job(
            idemp=req.idempotency_key,
            source=req.source,
            type_=req.type,
            priority=req.priority or "medium",
            timestamp=req.timestamp or "",
            payload_json=json.dumps(req.payload, ensure_ascii=False),
        )
    hub_req = legacy_to_hub(req)
    eid = record_event(service=hub_req.service, action=hub_req.action, params=hub_req.params.model_dump(), job_id=hub_req.job_id)
    return HubExecuteResponse(ok=True, event_id=eid, job_id=hub_req.job_id)
