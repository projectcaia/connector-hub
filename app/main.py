
from fastapi import FastAPI
from .routers import hub, bridge

app = FastAPI(title="ConnectorHub (Clean)")
app.include_router(hub.router)
app.include_router(bridge.router)

@app.get("/health")
def health():
    return {"ok": True}
