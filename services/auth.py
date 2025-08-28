import os
from fastapi import HTTPException, status

def require_bearer(auth_header: str | None):
    secret = os.getenv("CONNECTOR_SECRET")
    if not secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="server not configured")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
    token = auth_header.split(None, 1)[1]
    if token != secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")
