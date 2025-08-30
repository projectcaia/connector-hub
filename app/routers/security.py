
from fastapi import HTTPException
from typing import Optional
import os

def verify_bearer(authorization: str):
    # Expect "Bearer <token>"
    try:
        scheme, token = authorization.split(" ", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    expected = os.getenv("CONNECTOR_SECRET") or os.getenv("CONNECTOR_HUB_SECRET") or ""
    if not expected:
        # Allow passing with explicit sentinel_* token as fallback (legacy env)
        expected = os.getenv("CONNECTOR_SECRET_FALLBACK", "")
    if expected and token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
