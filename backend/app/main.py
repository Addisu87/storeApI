from contextlib import asynccontextmanager  # noqa: D100
from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket

from app.api.main import api_router
from app.core.config import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: D103
    # Startup logic
    yield  # Application runs here
    # Shutdown logic
    with open("log.txt", mode="a") as log:
        log.write("Application shutdown\n")


# Initialize FastAPI application
# Metadata for API
app = FastAPI(lifespan=lifespan)

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


@app.websocket("/ws")
async def websocket(websocket: WebSocket):  # noqa: D103
    await websocket.accept()
    await websocket.send_json({"msg": "Hello WebSocket"})
    await websocket.close()
    await websocket.close()
