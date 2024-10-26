from fastapi import FastAPI
from .internal import admin
from app.routers import users, items

app = FastAPI()

app.include_router(users.router)
app.include_router(items.router)
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}