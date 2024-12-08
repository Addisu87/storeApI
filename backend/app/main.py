# Application entry point
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.api.main import api_router

# Initialize FastAPI application
app = FastAPI(
    title="My FastAPI Application",
    description="An example FastAPI application with CORS and routing.",
    version="1.0.0",
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


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint providing a simple health check or welcome message.
    """
    return {"message": "Hello Bigger Applications!"}
