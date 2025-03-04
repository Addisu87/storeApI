# Application entry point
from fastapi import APIRouter

from app.api.routes import auth, items, users
from app.api.routes.tasks import router as tasks_router

api_router = APIRouter()

api_router.include_router(items.router)
api_router.include_router(users.router)
api_router.include_router(auth.router)
api_router.include_router(tasks_router)
