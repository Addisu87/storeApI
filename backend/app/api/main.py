# Application entry point
from fastapi import APIRouter

from app.api.routes import items, login, notifications, users
from app.static import files

api_router = APIRouter()

api_router.include_router(items.router)
api_router.include_router(users.router)
api_router.include_router(login.router)
api_router.include_router(files.router)
api_router.include_router(notifications.router)
