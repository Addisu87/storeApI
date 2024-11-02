from fastapi import FastAPI
from .internal import admin
from api.routers import users, items
from api.auth import login

api = FastAPI()

api.include_router(items.router)
api.include_router(users.router)
api.include_router(login.router)
api.include_router(admin.router, prefix="/admin", tags=["admin"])


@api.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
