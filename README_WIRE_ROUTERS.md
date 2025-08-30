
# How to wire routers (if not already)
# In app/main.py:
#
# from fastapi import FastAPI
# from .routers import hub, bridge
#
# app = FastAPI()
# app.include_router(hub.router)
# app.include_router(bridge.router)
#
# That's it. Both /hub/execute and /bridge/ingest will be available.
