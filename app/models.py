
from __future__ import annotations
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field

# ---- New schema (/hub/execute) ----
class HubParams(BaseModel):
    source: str = Field(..., description="event source, e.g., 'sentinel'")
    type: str = Field(..., description="event type, e.g., 'alert.market'")
    event: str = Field(..., description="short title or event name")  # required to satisfy existing validators
    priority: Optional[str] = None
    timestamp: Optional[str] = None  # ISO8601 string
    payload: Dict[str, Any] = Field(default_factory=dict)

class HubExecuteRequest(BaseModel):
    service: str = Field(..., description="agent | mail | memory | github | ...")
    action: str = Field(..., description="notify | read | write | recall | ...")
    params: HubParams
    job_id: Optional[str] = None

class HubExecuteResponse(BaseModel):
    ok: bool
    event_id: Optional[int] = None
    job_id: Optional[str] = None

# ---- Legacy schema (/bridge/ingest) ----
class LegacyIngestRequest(BaseModel):
    idempotency_key: str
    source: str
    type: str
    priority: Optional[str] = None
    timestamp: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
