
from __future__ import annotations
from fastapi import APIRouter, Header, Request
from ..models import HubExecuteRequest, HubExecuteResponse
from ..deps import record_event
from .security import verify_bearer

router = APIRouter(prefix="/hub", tags=["hub"])

@router.post("/execute", response_model=HubExecuteResponse)
async def hub_execute(req: HubExecuteRequest, authorization: str = Header(...)):
    verify_bearer(authorization)
    eid = record_event(service=req.service, action=req.action, params=req.params.model_dump(), job_id=req.job_id)
    return HubExecuteResponse(ok=True, event_id=eid, job_id=req.job_id)
