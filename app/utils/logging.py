import os, json, sys, datetime

LEVELS = {"DEBUG": 10, "INFO": 20, "WARN": 30, "WARNING": 30, "ERROR": 40}
LOG_LEVEL = LEVELS.get(os.getenv("LOG_LEVEL", "INFO").upper(), 20)

def log(level: str, **fields):
    lvl = LEVELS.get(level.upper(), 20)
    if lvl < LOG_LEVEL:
        return
    payload = {"ts": datetime.datetime.utcnow().isoformat()+"Z", "lvl": level.upper()}
    payload.update(fields)
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()
