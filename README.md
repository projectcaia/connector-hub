
# ConnectorHub UltraClean (2025-08-30)
단일 목적/단일 엔드포인트 구조
- POST /hub/execute  (정식 알람/트리거 수신)
- GET  /events/query (최근 이벤트 조회)
- GET  /health       (헬스체크)

## 배포 전제
- DB_PATH=/data/hub.db
- CONNECTOR_SECRET=sentinel_20250818_abcd1234

## 테스트
### health
curl https://<HUB>/health

### execute (정상 바디)
curl -X POST "https://<HUB>/hub/execute" \
  -H "Authorization: Bearer sentinel_20250818_abcd1234" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data-binary @- <<'JSON'
{
  "service": "agent",
  "action": "notify",
  "params": {
    "source": "sentinel",
    "event": "센티넬 알람(테스트)",
    "summary": "ΔNQ -1.23%, Reflex LV1",
    "trigger": "Reflex",
    "level": "LV1",
    "meta": {"dryrun": true}
  },
  "job_id": "SN-NQ-TEST-ULTRACLEAN-001"
}
JSON

### query
curl -X GET "https://<HUB>/events/query?limit=5" -H "Authorization: Bearer sentinel_20250818_abcd1234"
