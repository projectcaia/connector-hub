
from __future__ import annotations
from typing import Optional
from .deps import get_db, ensure_schema

# ensure schema (jobs/events) — idempotent
ensure_schema(None)

def find_job_by_idemp(idemp: str) -> Optional[dict]:
    with get_db() as db:
        cur = db.execute("SELECT id FROM jobs WHERE idempotency_key = ?", (idemp,))
        row = cur.fetchone()
        return dict(row) if row else None

def upsert_job(idemp: str, source: str, type_: str, priority: str, timestamp: str, payload_json: str) -> int:
    with get_db() as db:
        db.execute(
            "INSERT OR IGNORE INTO jobs(idempotency_key, source, type, priority, timestamp, payload) VALUES(?,?,?,?,?,?)",
            (idemp, source, type_, priority, timestamp, payload_json),
        )
        cur = db.execute("SELECT id FROM jobs WHERE idempotency_key = ?", (idemp,))
        row = cur.fetchone()
        return row["id"] if row else 0
