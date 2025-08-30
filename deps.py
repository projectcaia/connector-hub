
"""
ConnectorHub deps.py (patched)
- Ensures SQLite schema on import (fixes missing 'job_id' in events table).
- Exposes get_db() and record_event() helpers.
Env:
  DB_PATH=/tmp/hub.db (default)  # recommend /data/hub.db in prod
"""
import os
import json
import sqlite3
from contextlib import contextmanager
from typing import Optional, Dict, Any

# --- Config ---
DB_PATH = os.getenv("DB_PATH", "/tmp/hub.db")

# --- Schema ensure (on import) ---
try:
    from connectorhub_db_patch import ensure_schema
except Exception as e:  # fallback if relative import
    # local fallback import if module path differs
    import importlib.util, sys, types
    spec = importlib.util.spec_from_file_location("connectorhub_db_patch", os.path.join(os.path.dirname(__file__), "connectorhub_db_patch.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["connectorhub_db_patch"] = mod
    spec.loader.exec_module(mod)  # type: ignore
    ensure_schema = mod.ensure_schema  # type: ignore

DB_PATH = ensure_schema(DB_PATH)

# --- SQLite helpers ---
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

# --- Domain helpers ---
def record_event(service: str, action: str, params: Dict[str, Any], job_id: Optional[str] = None) -> int:
    payload = json.dumps(params, ensure_ascii=False)
    with get_db() as db:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO events(service, action, params, job_id) VALUES(?, ?, ?, ?)",
            (service, action, payload, job_id),
        )
        return cur.lastrowid
