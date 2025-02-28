import logging

import sentry_sdk  # type: ignore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings

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

logger = logging.getLogger(__name__)


# Initialize FastAPI application
# Metadata for API
app = FastAPI(title=settings.PROJECT_NAME)

# Add CORS middleware
# This will allow the frontend to make requests to the backend.
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],  # Allows all HTTP methods
        allow_headers=["*"],  # Allows all headers
    )


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
