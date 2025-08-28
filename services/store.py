import os, json, sqlite3
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple

def _db_path() -> str:
    return os.getenv("DB_PATH") or "/data/connectorhub_events.db"

class Store:
    def __init__(self):
        self.path = _db_path()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def _connect(self):
        conn = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def ensure_schema(self):
        with self._connect() as db:
            db.execute(
                '''
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    ts TEXT NOT NULL,
                    service TEXT,
                    action TEXT,
                    source TEXT,
                    event TEXT,
                    trigger TEXT,
                    level TEXT,
                    summary TEXT,
                    payload TEXT
                )
                '''
            )
            db.commit()

    def insert_event(self, row: Dict[str, Any]) -> str:
        evt_id = "evt_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        with self._connect() as db:
            db.execute(
                "INSERT INTO events (id, ts, service, action, source, event, trigger, level, summary, payload) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    evt_id,
                    row.get("ts"),
                    row.get("service"),
                    row.get("action"),
                    row.get("source"),
                    row.get("event"),
                    row.get("trigger"),
                    row.get("level"),
                    row.get("summary"),
                    json.dumps(row.get("payload", {}), ensure_ascii=False),
                )
            )
            db.commit()
        return evt_id

    def query_events(self,
                     source: Optional[str],
                     event: Optional[str],
                     trigger: Optional[str],
                     level: Optional[str],
                     since, until, limit: int) -> List[Dict[str, Any]]:
        q = "SELECT * FROM events WHERE ts >= ? AND ts <= ?"
        args: List[Any] = [since.isoformat(), until.isoformat()]
        if source:
            q += " AND source = ?"; args.append(source)
        if event:
            q += " AND event = ?"; args.append(event)
        if trigger:
            q += " AND trigger = ?"; args.append(trigger)
        if level:
            q += " AND level = ?"; args.append(level)
        q += " ORDER BY ts DESC LIMIT ?"; args.append(limit)
        with self._connect() as db:
            rows = [dict(r) for r in db.execute(q, args).fetchall()]
        for r in rows:
            try:
                r["payload"] = json.loads(r["payload"]) if r.get("payload") else {}
            except Exception:
                r["payload"] = {}
        return rows
