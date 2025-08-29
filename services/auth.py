# services/auth.py
import os, hmac, hashlib, unicodedata
from fastapi import HTTPException, status


# 허용 가능한 ENV 키(어느 하나만 존재해도 통과 기준)
_ENV_KEYS = ("CONNECTOR_SECRET", "HUB_SECRET", "CONNECTOR_TOKEN")


def _get_secret() -> str | None:
for k in _ENV_KEYS:
v = os.getenv(k)
if v:
# 공백/개행/유니코드 정규화
v = unicodedata.normalize("NFC", v).strip()
if v:
return v
return None


def _ct_eq(a: str, b: str) -> bool:
try:
return hmac.compare_digest(a, b)
except Exception:
return False


def require_auth(raw_body: bytes, authorization: str | None, x_signature: str | None):
secret = _get_secret()
if not secret:
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="server not configured")


# 1) Bearer 토큰 경로
if authorization and authorization.lower().startswith("bearer "):
token = authorization.split(None, 1)[1]
token = unicodedata.normalize("NFC", token).strip()
if _ct_eq(token, secret):
return


# 2) HMAC 경로 (X-Signature)
if x_signature:
mac = hmac.new(secret.encode("utf-8"), raw_body or b"", hashlib.sha256).hexdigest()
if _ct_eq(mac, x_signature.strip()):
return


# 불일치 시 거부(로그는 상위 레벨에서 남김)
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
