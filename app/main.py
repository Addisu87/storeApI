# Application entry point
from fastapi import FastAPI


from .internal import admin
from app.routes import users, items
from app.auth import login
from app.static import static_files


app = FastAPI()

app.include_router(items.router)
app.include_router(users.router)
app.include_router(login.router)
app.include_router(static_files.router)
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
