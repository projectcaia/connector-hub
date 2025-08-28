from fastapi import FastAPI
from app.routers import health, bridge, jobs

app = FastAPI(title="Connector Hub", version="2025.08.25")

app.include_router(health.router)
app.include_router(bridge.router, prefix="/bridge")
app.include_router(jobs.router)
