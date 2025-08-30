
from fastapi import FastAPI
from .routers import hub, events

app = FastAPI(title="ConnectorHub (UltraClean)")
app.include_router(hub.router)
app.include_router(events.router)

@app.get("/health")
def health():
    return {"ok": True}
