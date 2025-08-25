import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator

DB_PATH = os.getenv("DB_PATH", "./data/hub.db")

def _ensure_db(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            '''CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                idempotency_key TEXT NOT NULL UNIQUE,
                source TEXT NOT NULL,
                type TEXT NOT NULL,
                priority TEXT,
                ts TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );'''
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_ts ON jobs(ts);")
        conn.execute(
            '''CREATE TABLE IF NOT EXISTS events (
                job_id TEXT NOT NULL,
                body_json TEXT NOT NULL,
                hmac TEXT NOT NULL,
                received_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            );'''
        )

@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    _ensure_db(DB_PATH)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()
