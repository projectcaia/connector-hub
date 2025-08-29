# connectorhub_routers/hub.py
from datetime import datetime, timezone
from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from services.auth import require_auth
from services.store import Store
from services.notify import TelegramNotifier
from services.forward import ConnectorGPTForwarder
from services.ersp import build_ersp

router = APIRouter()

class ExecuteParams(BaseModel):
    source: str
    event: str
    summary: Optional[str] = None
    trigger: Optional[str] = None
    level: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class ExecuteBody(BaseModel):
    service: str = Field(pattern=r"^(agent|mail|memory|github)$")
    action: str = Field(pattern=r"^(notify|read|write|recall)$")
    params: ExecuteParams

@router.post("/execute")
async def execute(
    body: ExecuteBody,
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_signature: Optional[str] = Header(default=None),
):
    # HMAC 계산을 위해 원문 바디 확보(Starlette가 캐시해서 안전)
    raw = await request.body()
    require_auth(raw, authorization, x_signature)

    now = datetime.now(timezone.utc).isoformat()
    store = Store()
    store.ensure_schema()

    row = {
        "ts": now,
        "service": body.service,
        "action": body.action,
        "source": body.params.source,
        "event": body.params.event,
        "trigger": body.params.trigger,
        "level": body.params.level,
        "summary": body.params.summary,
        "payload": {
            "meta": body.params.meta or {},
            "client": request.client.host if request.client else None,
        },
    }

    evt_id = store.insert_event(row)
    ersp = build_ersp(row)

    notifier = TelegramNotifier.from_env()
    gpt_fwd = ConnectorGPTForwarder.from_env()

    broadcast = {"telegram": False, "connector_gpt": False}
    try:
        if notifier:
            notifier.send_message(
                title=f"[에이전트 알림] {row['source']}",
                message=f"{row['event']} – {row.get('summary') or ''} (트리거: {row.get('trigger')}, 레벨: {row.get('level')})",
            )
            broadcast["telegram"] = True
    except Exception:
        pass

    try:
        if gpt_fwd:
            gpt_fwd.forward_summary(evt_id=evt_id, row=row, ersp=ersp)
            broadcast["connector_gpt"] = True
    except Exception:
        pass

    return {"ok": True, "id": evt_id, "stored": True, "broadcast": broadcast, "ersp": ersp}
