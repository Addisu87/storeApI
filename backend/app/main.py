import logging
from contextlib import asynccontextmanager

import sentry_sdk  # type: ignore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.deps import engine
from app.database.db import Session, init_db

logger = logging.getLogger(__name__)

sentry_sdk.init(
    dsn=str(settings.SENTRY_DSN),
    enable_tracing=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database synchronously
    with Session(engine) as session:
        init_db(session)
    yield


app = FastAPI(lifespan=lifespan, title=settings.PROJECT_NAME)

# Add CORS middleware
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(api_router)
