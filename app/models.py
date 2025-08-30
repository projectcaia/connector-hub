
from __future__ import annotations
from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field

class HubParams(BaseModel):
    source: str = Field(..., description="event source (e.g., 'sentinel')")
    event: str = Field(..., description="short title / name of the event")
    summary: Optional[str] = None
    trigger: Optional[str] = None
    level: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class HubExecuteRequest(BaseModel):
    service: str = Field(..., description="agent | mail | memory | github | ...")
    action: str = Field(..., description="notify | read | write | recall | ...")
    params: HubParams
    job_id: Optional[str] = None

class HubExecuteResponse(BaseModel):
    ok: bool
    event_id: Optional[int] = None
    job_id: Optional[str] = None

class EventRow(BaseModel):
    id: int
    service: str
    action: str
    params: Dict[str, Any]
    job_id: Optional[str] = None
    created_at: str
