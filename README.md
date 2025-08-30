
# ConnectorHub Minimal Clean (2025-08-30)
- 중복 파일 제거, 라우트 단일화
- `/hub/execute` (신규) + `/bridge/ingest` (레거시 호환) 동시에 제공
- `params.event` 필드 요구사항 반영 → 422 차단
- DB 스키마 자동 보정: events + jobs (+ 인덱스)

## 적용법
1) 레포 루트에 압축 해제(덮어쓰기 허용)
2) 환경변수
   - DB_PATH=/data/hub.db
   - CONNECTOR_SECRET=sentinel_20250818_abcd1234
3) 재배포/재시작
4) 확인
   - GET /health → {"ok": true}
   - POST /bridge/ingest (레거시 바디)
   - POST /hub/execute (신규 바디)

## 테스트 예시
### legacy → /bridge/ingest
curl -X POST "$HUB/bridge/ingest"   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json; charset=utf-8"   --data-binary @- <<'JSON'
{
  "idempotency_key": "SN-NQ-TEST-001",
  "source": "sentinel",
  "type": "alert.market",
  "priority": "medium",
  "timestamp": "2025-08-30T20:59:00+09:00",
  "payload": {
    "index": "NQ",
    "level": "LV1",
    "delta_pct": -1.23,
    "note": "센티넬 테스트: 나스닥 선물 레벨 감지",
    "original_ts": "2025-08-30T20:59:00+09:00"
  }
}
JSON

### new → /hub/execute
curl -X POST "$HUB/hub/execute"   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json; charset=utf-8"   --data-binary @- <<'JSON'
{
  "service": "agent",
  "action": "notify",
  "params": {
    "source": "sentinel",
    "type": "alert.market",
    "event": "센티넬 알람(테스트)",
    "priority": "medium",
    "timestamp": "2025-08-30T20:59:00+09:00",
    "payload": {
      "index": "NQ",
      "level": "LV1",
      "delta_pct": -1.23,
      "note": "센티넬 테스트: 나스닥 선물 레벨 감지",
      "original_ts": "2025-08-30T20:59:00+09:00"
    }
  },
  "job_id": "SN-NQ-TEST-002"
}
JSON
