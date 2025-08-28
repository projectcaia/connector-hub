from fastapi import FastAPI
from app.routers import health, bridge, jobs, judge, events


app = FastAPI(title="Connector Hub", version="2025.08.28")


# 기존 라우터
app.include_router(health.router)
app.include_router(bridge.router, prefix="/bridge")
app.include_router(jobs.router)


# 신규 라우터 (Embedded Caia)
app.include_router(judge.router) # POST /judge
app.include_router(events.router) # GET /events/recent
