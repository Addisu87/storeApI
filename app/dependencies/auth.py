# Authentication/authorization dependencies
# Reusable components for security in routes.

from typing import Annotated
from fastapi import APIRouter, Depends, Cookie, Header, HTTPException

router = APIRouter()


# Dependencies in path operation decorators-
async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


# Global Dependencies
router = APIRouter(dependencies=[Depends(verify_token), Depends(verify_key)])
