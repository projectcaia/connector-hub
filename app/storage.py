import json
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import sqlite3

from app.models import IngestBody
from app.deps import get_db

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _make_job_id(ts: str) -> str:
    # simple sortable id
    safe = ts.replace(":", "").replace("-", "").replace(".", "")
    return f"job_{safe}"

def find_job_by_idemp(idemp: str) -> Optional[str]:
    with get_db() as conn:
        cur = conn.execute("SELECT id FROM jobs WHERE idempotency_key = ?", (idemp,))
        row = cur.fetchone()
        return row[0] if row else None

def insert_job(key: str, body: IngestBody, hmac_hex: str) -> str:
    jid = _make_job_id(body.timestamp)
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO jobs (id, idempotency_key, source, type, priority, ts) VALUES (?,?,?,?,?,?)",
                (jid, key, body.source, body.type, body.priority, body.timestamp),
            )
            conn.execute(
                "INSERT INTO events (job_id, body_json, hmac, received_at) VALUES (?,?,?,datetime('now'))",
                (jid, json.dumps(body.model_dump()), hmac_hex),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # idempotency duplicate or primary key conflict
            pass
    return jid

def fetch_recent_jobs(hours: int = 24) -> List[Dict[str, Any]]:
    threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
    tiso = threshold.isoformat()
    with get_db() as conn:
        cur = conn.execute(
            "SELECT id, idempotency_key, type, priority, ts FROM jobs WHERE ts >= ? ORDER BY ts DESC",
            (tiso,),
        )
        items = []
        for row in cur.fetchall():
            items.append({
                "id": row[0],
                "idempotency_key": row[1],
                "type": row[2],
                "priority": row[3],
                "timestamp": row[4],
            })
        return items
