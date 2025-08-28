# === main.py (완전본) ===
from fastapi import FastAPI
from app.routers import health, bridge, jobs, judge, events

app = FastAPI(title="Connector Hub", version="2025.08.28")

# 기존 라우터
app.include_router(health.router)
app.include_router(bridge.router, prefix="/bridge")
app.include_router(jobs.router)

# 신규 라우터 (Embedded Caia)
app.include_router(judge.router)            # POST /judge
app.include_router(events.router)           # GET  /events/recent


# === app/routers/judge.py (신규) ===
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.security import verify_hmac
from app.storage import upsert_job

router = APIRouter()

class JudgeIn(BaseModel):
    type: str
    source: str
    actor: Optional[str] = "system"
    trace_id: str
    timestamp: str
    payload: dict

@router.post("/judge")
def judge(
    body: JudgeIn,
    x_signature: Optional[str] = Header(default=None, convert_underscores=True),
    idempotency_key: Optional[str] = Header(default=None, convert_underscores=True),
):
    if not x_signature or not verify_hmac(x_signature, body.dict()):
        raise HTTPException(status_code=401, detail="Invalid signature")

    final_text = f"[{body.type}] from {body.source} · trace={body.trace_id}"
    ersp = {
        "event": body.type,
        "interpretation": "Embedded judgement stub.",
        "lesson": "Ensure HMAC and log summary.",
        "if_then": "If repeated, raise priority."
    }
    out = {
        "ok": True,
        "ersp": ersp,
        "action": "JUST_REPLY",
        "final_text": final_text,
        "trace_id": body.trace_id
    }
    # 저장 (요약)
    upsert_job(
        job_id=f"job_{body.timestamp.replace(':','').replace('-','')}",
        idempotency_key=idempotency_key or body.trace_id,
        type=body.type,
        timestamp=body.timestamp,
        summary=final_text,
        source=body.source,
    )
    return out


# === app/routers/events.py (신규) ===
from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from app.storage import recent_jobs

router = APIRouter()

@router.get("/events/recent")
def events_recent(limit: int = 3, x_signature: Optional[str] = Header(default=None, convert_underscores=True)):
    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    items = recent_jobs(limit=limit)
    return {"items": items}


# === 패키지 초기화 파일 (없으면 생성) ===
# app/__init__.py      → 빈 파일로 존재
# app/routers/__init__.py → 빈 파일로 존재


# === Railway ENV 예시 ===
# CONNECTOR_SECRET=sentinel_20250818_abcd1234
# OPENAI_API_KEY=sk-... (선택)
# APP_VERSION=2025.08.28
# ENFORCE_HMAC_READY=true (선택)


# === 테스트 커맨드 ===
# export CONNECTOR_SECRET='sentinel_20250818_abcd1234'
# export BODY='{"type":"alert.market","source":"sentinel","actor":"system","trace_id":"test-judge-001","timestamp":"2025-08-28T02:10:00Z","payload":{"dK200":-1.7,"VIX":6}}'
# SIG=$(python - <<'PY'
# import os,hmac,hashlib
# print(hmac.new(os.environ["CONNECTOR_SECRET"].encode(), os.environ["BODY"].encode(), hashlib.sha256).hexdigest())
# PY
# )
# curl -s -X POST "https://connector-hub-production.up.railway.app/judge" -H "Content-Type: application/json" -H "X-Signature: $SIG" -H "Idempotency-Key: test-judge-001" -d "$BODY"
# curl -s "https://connector-hub-production.up.railway.app/events/recent?limit=3" -H "X-Signature: $SIG"
