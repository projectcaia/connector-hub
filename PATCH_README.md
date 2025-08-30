
# ConnectorHub DB Patch (2025-08-30)

이 패치는 `/bridge/ingest` 처리 시 발생한 `sqlite3.OperationalError: 테이블 events에 job_id라는 열이 없습니다.` 문제를 해결합니다.

## 구성 파일
- `deps.py` (교체용): 모듈 import 시 자동으로 DB 스키마를 보정합니다.
- `connectorhub_db_patch.py`: 스키마 보정 로직 (독립 실행/임포트 모두 가능)
- `PATCH_README.md`: 본 안내

## 적용 방법 (권장: 교체)
1. 기존 리포지토리에서 `deps.py`를 **이 패치의 `deps.py`로 교체**합니다.
2. 리포지토리 루트(또는 `deps.py`와 같은 디렉토리)에 `connectorhub_db_patch.py`를 추가합니다.
3. 컨테이너 재시작.

> 별도 코드 수정 없이, `deps.py` import 시 자동으로 `events` 테이블 스키마를 보정합니다.

## 환경 변수
- `DB_PATH` (기본 `/tmp/hub.db`) — 운영환경에서는 `/data/hub.db` 경로 사용을 권장합니다.
  - 예: `DB_PATH=/data/hub.db`

## 확인
- 컨테이너 기동 로그에 아래 메시지가 보이면 정상 적용입니다.
  - `[PATCH] Added missing column: job_id to events` (최초 1회)
  - `[PATCH] DB schema ensured successfully at ...`
