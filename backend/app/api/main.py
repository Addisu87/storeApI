# Application entry point
from fastapi import APIRouter


from app.api.internal import admin
from app.api.routes import users, items, heroes
from app.api.routes.auth import login
from app.static import static_files


api_router = APIRouter()

api_router.include_router(items.router)
api_router.include_router(users.router)
api_router.include_router(heroes.router)
api_router.include_router(login.router)
api_router.include_router(static_files.router)
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
