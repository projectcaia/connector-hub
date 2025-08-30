import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "/tmp/hub.db")

# 필요한 컬럼 정의
table_defs = {
    "events": [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("service", "TEXT"),
        ("action", "TEXT"),
        ("params", "TEXT"),
        ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("job_id", "TEXT")  # 누락된 컬럼 추가
    ]
}

def ensure_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 테이블 생성 또는 변경
    for table, columns in table_defs.items():
        # 테이블 없으면 새로 생성
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                {', '.join([col + ' ' + dtype for col, dtype in columns if col != 'job_id'])}
            )
        """)

        # 컬럼 존재 여부 확인 후 없으면 추가
        cursor.execute(f"PRAGMA table_info({table})")
        existing_cols = [row[1] for row in cursor.fetchall()]

        for col, dtype in columns:
            if col not in existing_cols:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
                print(f"[PATCH] Added missing column: {col} to {table}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    ensure_schema()
    print("[PATCH] DB schema ensured successfully.")
