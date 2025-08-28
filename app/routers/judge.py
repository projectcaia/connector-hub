# === 2) app/routers/judge.py (신규, 전체 붙여넣기) ===
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
upsert_job(
job_id=f"job_{body.timestamp.replace(':','').replace('-','')}",
idempotency_key=idempotency_key or body.trace_id,
type=body.type,
timestamp=body.timestamp,
summary=final_text,
source=body.source,
)
return out
