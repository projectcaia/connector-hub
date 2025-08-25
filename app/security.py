import os, hmac, hashlib

SECRET = os.getenv("CONNECTOR_SECRET", "")

def verify_signature(raw_body: bytes, x_signature: str | None) -> bool:
    if not x_signature or not SECRET:
        return False
    mac = hmac.new(SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    # constant-time compare
    try:
        return hmac.compare_digest(mac, x_signature)
    except Exception:
        return False
