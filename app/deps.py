import os
base = os.path.dirname(__file__)
patch_path = os.path.join(base, "connectorhub_db_patch.py")
spec = importlib.util.spec_from_file_location("connectorhub_db_patch", patch_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["connectorhub_db_patch"] = mod
assert spec.loader is not None
spec.loader.exec_module(mod) # type: ignore
return mod.ensure_schema # type: ignore


ensure_schema = _load_patch()
DB_PATH = ensure_schema(os.getenv("DB_PATH")) # import 시점 자동 보정




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




# (선택) 공용 insert helper — 기존 코드에서 사용 중이면 재사용
import json


def record_event(service: str, action: str, params: dict, job_id: str | None = None) -> int:
payload = json.dumps(params, ensure_ascii=False)
with get_db() as db:
cur = db.cursor()
cur.execute(
"INSERT INTO events(service, action, params, job_id) VALUES(?, ?, ?, ?)",
(service, action, payload, job_id),
)
return cur.lastrowid
