
import os
from fastapi import HTTPException

def verify_bearer(authorization: str):
    try:
        scheme, token = authorization.split(" ", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    expected = os.getenv("CONNECTOR_SECRET") or os.getenv("CONNECTOR_HUB_SECRET") or ""
    if expected and token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
