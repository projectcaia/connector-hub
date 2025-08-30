"""
Modified deps.py for ConnectorHub.

This patch ensures that the SQLite schema for the `events` table matches the
expected schema. If an existing `events` table does not contain the required
`job_id` column (e.g., from an old version), it will be dropped and
recreated. This prevents runtime errors like:

    sqlite3.OperationalError: no such column: job_id

Usage:
Replace the original `app/deps.py` in the connector-hub repository with this
file and redeploy. The rest of the application remains unchanged.
"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator

# Use persistent DB path if provided, fallback to ./data/hub.db
DB_PATH = os.getenv("DB_PATH", "./data/hub.db")

def _ensure_db(path: str) -> None:
    """Ensure that the SQLite database exists and has the correct schema.

    This function creates the `jobs` and `events` tables if they do not
    exist. Additionally, it inspects the existing `events` table and drops
    it if the required `job_id` column is missing (to handle schema
    migrations from older versions). After any necessary cleanup, it
    recreates the `events` table with the correct columns and foreign key.

    Args:
        path: Path to the SQLite database file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with sqlite3.connect(path) as conn:
        # Enable WAL mode for concurrent reads/writes
        conn.execute("PRAGMA journal_mode=WAL;")

        # Create jobs table
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
        # Index on timestamp for faster queries
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_ts ON jobs(ts);")

        # Check existing events table schema
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events';")
        exists = cur.fetchone() is not None
        needs_recreate = False
        if exists:
            cols_info = conn.execute("PRAGMA table_info(events);").fetchall()
            col_names = [c[1] for c in cols_info]
            # If job_id column is missing, mark for recreation
            if 'job_id' not in col_names:
                needs_recreate = True
        
        if needs_recreate:
            conn.execute("DROP TABLE IF EXISTS events;")

        # Create events table (idempotent)
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
    """Context manager that yields a SQLite connection with correct schema."""
    _ensure_db(DB_PATH)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()