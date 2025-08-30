import os
("priority", "TEXT"),
("timestamp", "TEXT"), # ISO8601 문자열 저장
("payload", "TEXT"), # JSON 직렬화 텍스트
("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
]
}


INDEXES = [
("jobs", "idx_jobs_idempotency", "UNIQUE(idempotency_key)"),
("jobs", "idx_jobs_created_at", "created_at"),
("events", "idx_events_created_at", "created_at"),
]


def _create_table_if_missing(cur: sqlite3.Cursor, table: str, columns: list[tuple[str, str]]):
cols_def = ", ".join([f"{c} {t}" for c, t in columns])
cur.execute(f"""
CREATE TABLE IF NOT EXISTS {table} (
{cols_def}
)
""")




def _add_missing_columns(cur: sqlite3.Cursor, table: str, columns: list[tuple[str, str]]):
cur.execute(f"PRAGMA table_info({table})")
existing = {row[1] for row in cur.fetchall()}
for col, dtype in columns:
if col not in existing:
cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
print(f"[PATCH] Added missing column: {col} to {table}")




def _create_indexes(cur: sqlite3.Cursor):
for table, name, expr in INDEXES:
cur.execute(
f"CREATE INDEX IF NOT EXISTS {name} ON {table}({expr})"
)




def ensure_schema(db_path: str | None = None) -> str:
path = db_path or os.getenv("DB_PATH", DB_DEFAULT)
os.makedirs(os.path.dirname(path), exist_ok=True)
with closing(sqlite3.connect(path)) as conn:
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA busy_timeout=5000")
cur = conn.cursor()
# 테이블 생성 및 누락 컬럼 보강
for table, columns in TABLES.items():
_create_table_if_missing(cur, table, columns)
_add_missing_columns(cur, table, columns)
# 인덱스 생성
_create_indexes(cur)
conn.commit()
return path


if __name__ == "__main__":
p = ensure_schema()
print(f"[PATCH] DB schema ensured successfully at {p}")
