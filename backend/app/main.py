# Application entry point
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.api.main import api_router

from app.core.db import create_db_and_tables


# Initialize FastAPI application
# Metadata for API
app = FastAPI(
    title="FastAPI Application",
    description="An example FastAPI application with CORS and routing.",
    version="1.0.0",
    contact={
        "name": "Addisu Haile",
        "url": "https://portfolio-addisu-addisu87.vercel.app/",
        "email": "addisuhaile87@gmail.com"
    },
    license_info={
        "name": "Apache 2.0",
        "identifier": "MIT",
    },
)


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


# Create Database Tables on Startup
@app.on_event("startup")
async def on_startup():
    create_db_and_tables()


@app.on_event("shutdown")
def shutdown_event():
    with open("log.txt", mode="a") as log:
        log.write("Application shutdown")


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint providing a simple health check or welcome message.
    """
    return {"message": "Hello Bigger Applications!"}
