from contextlib import asynccontextmanager  # noqa: D100
from functools import lru_cache
from typing import Annotated

from app.api.main import api_router
from app.core.config import Settings
from app.core.db import create_db_and_tables
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: D103
    # Startup logic
    create_db_and_tables()
    yield  # Application runs here
    # Shutdown logic
    with open("log.txt", mode="a") as log:
        log.write("Application shutdown\n")


# Initialize FastAPI application
# Metadata for API
app = FastAPI(
    title="FastAPI Application",
    description="An example FastAPI application with CORS and routing.",
    version="1.0.0",
    contact={
        "name": "Addisu Haile",
        "url": "https://portfolio-addisu-addisu87.vercel.app/",
        "email": "addisuhaile87@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "identifier": "MIT",
    },
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="files")


# CORS settings
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # In production, specify domains explicitly
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)


# Include API routes
app.include_router(api_router)


# instead of computing it again,
# executing the code of the function every time
@lru_cache
def get_settings():  # noqa: D103
    return Settings()  # type: ignore


# Root endpoint
@app.get("/", response_class=JSONResponse)
async def main():  # noqa: D103
    return {"msg": "Hello Bigger Applications!"}


@app.get("/info")
async def info(settings: Annotated[Settings, Depends(get_settings)]):  # noqa: D103
    return {
        "project_name": settings.project_name,
        "admin_email": settings.admin_email,
        "items_per_user": settings.items_per_user,
    }


@app.websocket("/ws")
async def websocket(websocket: WebSocket):  # noqa: D103
    await websocket.accept()
    await websocket.send_json({"msg": "Hello WebSocket"})
    await websocket.close()
    await websocket.close()
