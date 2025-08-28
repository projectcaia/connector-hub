from fastapi import FastAPI
from connectorhub_routers import hub, events_query, health

APP_VERSION = "2025.08.28a"  # hotfix

app = FastAPI(title="ConnectorHub Extension", version=APP_VERSION)

# NOTE: hub/events_query/health are APIRouter instances exported by connectorhub_routers.__init__
app.include_router(health)
app.include_router(hub, prefix="/hub")
app.include_router(events_query, prefix="/events")
