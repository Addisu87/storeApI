import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.deps import engine
from app.database.db import Session, init_db

logger = logging.getLogger(__name__)

# Configure Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=str(settings.SENTRY_DSN),
        enable_tracing=True,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    with Session(engine) as session:
        init_db(session)
    yield
    # Cleanup
    if engine:
        engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    # Use getattr with a default value to handle missing VERSION
    version=getattr(settings, "VERSION", "0.1.0"),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/")
async def root():
    return {"msg": "Hello Bigger Applications!"}

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    await websocket.send_json({"msg": "Hello WebSocket"})
    await websocket.close()
