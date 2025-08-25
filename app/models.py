from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class IngestBody(BaseModel):
    idempotency_key: Optional[str] = Field(default=None)
    source: str
    type: str
    priority: Optional[str] = None
    timestamp: str
    payload: Dict[str, Any]
