
from __future__ import annotations
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from typing import Optional
from .security import verify_bearer
from ..models import HubExecuteRequest, HubExecuteResponse
from ..deps import record_event, get_db

router = APIRouter(prefix="/hub", tags=["hub"])

@router.post("/execute", response_model=HubExecuteResponse)
async def hub_execute(req: HubExecuteRequest, request: Request, authorization: str = Header(...)):
    verify_bearer(authorization)  # raise 401 on invalid
    # Persist event (idempotency is handled at legacy layer; here we just store event)
    eid = record_event(service=req.service, action=req.action, params=req.params.model_dump(), job_id=req.job_id)
    return HubExecuteResponse(ok=True, event_id=eid, job_id=req.job_id)
