
import os, sqlite3
from contextlib import closing

DB_DEFAULT = "/data/hub.db"

TABLES = {
    "events": [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("service", "TEXT"),
        ("action", "TEXT"),
        ("params", "TEXT"),
        ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("job_id", "TEXT")
    ]
}

INDEXES = [
    ("events", "idx_events_created_at", "created_at")
]

def _create_table_if_missing(cur, table, columns):
    cols_def = ", ".join([f"{c} {t}" for c, t in columns])
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            {cols_def}
        )
    """)

def _add_missing_columns(cur, table, columns):
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cur.fetchall()}
    for col, dtype in columns:
        if col not in existing:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
            print(f"[PATCH] Added missing column: {col} to {table}")

def _create_indexes(cur):
    for table, name, expr in INDEXES:
        cur.execute(f"CREATE INDEX IF NOT EXISTS {name} ON {table}({expr})")

def ensure_schema(db_path: str | None = None) -> str:
    path = db_path or os.getenv("DB_PATH", DB_DEFAULT)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        cur = conn.cursor()
        for table, columns in TABLES.items():
            _create_table_if_missing(cur, table, columns)
            _add_missing_columns(cur, table, columns)
        _create_indexes(cur)
        conn.commit()
    return path

if __name__ == "__main__":
    p = ensure_schema()
    print(f"[PATCH] DB schema ensured successfully at {p}")
