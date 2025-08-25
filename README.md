# Connector Hub (FastAPI + SQLite + HMAC + Idempotency)

- Endpoints:
  - `GET /ready` – liveness/version
  - `GET /health` – DB connectivity
  - `POST /bridge/ingest` – HMAC verify + schema validate + idempotent store
  - `GET /jobs` – last 24h events (JSON)

## Quickstart (Docker)

```bash
docker build -t connector-hub:latest .
docker run --rm -it -p 8080:8080 -e CONNECTOR_SECRET=sentinel_20250818_abcd1234 -v $(pwd)/data:/data connector-hub:latest
# open http://localhost:8080/ready
```

## Railway Variables
```
CONNECTOR_SECRET=sentinel_20250818_abcd1234
DB_PATH=/data/hub.db
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO
```

## Curl test (domain example)
```bash
export HUB=https://fastapi-sentinel-production.up.railway.app
curl -sS $HUB/ready | jq .
curl -sS $HUB/health | jq .
export CONNECTOR_SECRET='sentinel_20250818_abcd1234'
export BODY='{"idempotency_key":"uuid-1","source":"sentinel","type":"alert.market","priority":"high","timestamp":"2025-08-25T10:44:31.816912","payload":{"rule":"iv_spike","index":"KOSPI200","level":"LV2","metrics":{"dK200":1.6,"dVIX":7.2}}}'
SIG=$(python - <<'PY'
import os,hmac,hashlib
print(hmac.new(os.environ["CONNECTOR_SECRET"].encode(), os.environ["BODY"].encode(), hashlib.sha256).hexdigest())
PY
)
curl -sS -X POST $HUB/bridge/ingest -H "Content-Type: application/json" -H "X-Signature: $SIG" -H "Idempotency-Key: uuid-1" --data "$BODY" | jq .
curl -sS -X POST $HUB/bridge/ingest -H "Content-Type: application/json" -H "X-Signature: $SIG" -H "Idempotency-Key: uuid-1" --data "$BODY" | jq .
curl -sS $HUB/jobs | jq .
```
