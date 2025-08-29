# services/auth.py
import os, hmac, hashlib, unicodedata
from fastapi import HTTPException, status
from typing import Optional

# 여러 환경키 허용 (운영 편의)
_ENV_KEYS = ("CONNECTOR_SECRET", "HUB_SECRET", "CONNECTOR_TOKEN")

def _get_secret() -> Optional[str]:
    for k in _ENV_KEYS:
        v = os.getenv(k)
        if v:
            v = unicodedata.normalize("NFC", v).strip()
            if v:
                return v
    return None

def _ct_eq(a: str, b: str) -> bool:
    try:
        return hmac.compare_digest(a, b)
    except Exception:
        return False

def require_auth(raw_body: bytes, authorization: Optional[str], x_signature: Optional[str]):
    """통합 인증: Bearer 또는 HMAC(X-Signature) 수용"""
    secret = _get_secret()
    if not secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="server not configured")

    # 1) Bearer 경로
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(None, 1)[1]
        token = unicodedata.normalize("NFC", token).strip()
        if _ct_eq(token, secret):
            return

    # 2) HMAC 경로
    if x_signature:
        mac = hmac.new(secret.encode("utf-8"), raw_body or b"", hashlib.sha256).hexdigest()
        if _ct_eq(mac, x_signature.strip()):
            return

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")


# ---- 호환용 shim (구버전 import 유지용) ----
def require_bearer(authorization: Optional[str]):
    """
    기존 코드가 from services.auth import require_bearer 를 사용할 때를 위한
    호환 레이어. Bearer만 검사(원문 바디 불필요).
    """
    return require_auth(b"", authorization, None)
