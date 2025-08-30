
import os, sqlite3, json
from contextlib import contextmanager

def _load_patch():
    try:
        from connectorhub_db_patch import ensure_schema  # type: ignore
        return ensure_schema
    except Exception:
        import importlib.util, sys
        base = os.path.dirname(__file__)
        patch_path = os.path.join(base, "connectorhub_db_patch.py")
        spec = importlib.util.spec_from_file_location("connectorhub_db_patch", patch_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["connectorhub_db_patch"] = mod
        assert spec.loader is not None
        spec.loader.exec_module(mod)  # type: ignore
        return mod.ensure_schema  # type: ignore

ensure_schema = _load_patch()
DB_PATH = ensure_schema(os.getenv("DB_PATH"))  # idempotent

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn

@contextmanager
def get_db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def record_event(service: str, action: str, params: dict, job_id: str | None = None) -> int:
    payload = json.dumps(params, ensure_ascii=False)
    with get_db() as db:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO events(service, action, params, job_id) VALUES(?, ?, ?, ?)",
            (service, action, payload, job_id),
        )
        return cur.lastrowid

def list_events(limit: int = 10):
    with get_db() as db:
        cur = db.execute(
            "SELECT id, service, action, params, job_id, created_at FROM events ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        out = []
        for r in rows:
            try:
                p = json.loads(r["params"] or "{}")
            except Exception:
                p = {"_raw": r["params"]}
            out.append({
                "id": r["id"],
                "service": r["service"],
                "action": r["action"],
                "params": p,
                "job_id": r["job_id"],
                "created_at": r["created_at"],
            })
        return out
