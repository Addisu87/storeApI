from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .internal import admin
from api.routers import users, items
from api.auth import login
from api.static import static_files
from api.dependencies import CommonQueryParams

api = FastAPI()

api.include_router(items.router, dependencies=[Depends(CommonQueryParams)])
api.include_router(users.router, dependencies=[Depends(CommonQueryParams)])
api.include_router(login.router)
api.include_router(static_files.router)
api.include_router(admin.router, prefix="/admin", tags=["admin"])


@api.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"message": str(exc.detail)}
    )


@api.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    print(f"OMG! An HTTP error!: {repr(exc)}")
    # return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
    return await http_exception_handler(request, exc)


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMG! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@api.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
