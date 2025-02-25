# Application entry point
from fastapi import APIRouter

from app.api.internal import admin
from app.api.routes import heroes, items, login, notifications, users
from app.static import files

api_router = APIRouter()

api_router.include_router(items.router)
api_router.include_router(users.router)
api_router.include_router(heroes.router)
api_router.include_router(login.router)
api_router.include_router(files.router)
api_router.include_router(notifications.router)
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
