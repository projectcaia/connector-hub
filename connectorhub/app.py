-import os
-from fastapi import FastAPI
-from connectorhub_routers import hub, events_query, health
-
-APP_VERSION = "2025.08.28"
-
-app = FastAPI(title="ConnectorHub Extension", version=APP_VERSION)
-app.include_router(health.router)
-app.include_router(hub.router, prefix="/hub")
-app.include_router(events_query.router, prefix="/events")
+import os
+from fastapi import FastAPI
+from connectorhub_routers import hub, events_query, health
+
+APP_VERSION = "2025.08.28a"  # hotfix
+
+app = FastAPI(title="ConnectorHub Extension", version=APP_VERSION)
+# NOTE: hub/events_query/health는 이미 APIRouter 객체임 (.__init__에서 router를 export)
+app.include_router(health)
+app.include_router(hub, prefix="/hub")
+app.include_router(events_query, prefix="/events")
