# Application entry point
from fastapi import APIRouter

from app.api.routes import auth, items, tasks, users
from app.core.config import settings

api_router = APIRouter(prefix=settings.API_V1_STR)

api_router.include_router(items.router)
api_router.include_router(users.router)
api_router.include_router(auth.router)
api_router.include_router(tasks.router)
