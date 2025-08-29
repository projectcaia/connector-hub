import os, hmac, hashlib, unicodedata
from fastapi import HTTPException, status

_ENV_KEYS = ("CONNECTOR_SECRET", "HUB_SECRET", "CONNECTOR_TOKEN")

def _get_secret() -> str | None:
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

def require_auth(raw_body: bytes, authorization: str | None, x_signature: str | None):
    secret = _get_secret()
    if not secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="server not configured")

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(None, 1)[1]
        token = unicodedata.normalize("NFC", token).strip()
