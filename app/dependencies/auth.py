# Authentication/authorization dependencies
# Reusable components for security in routes.

from typing import Annotated

from fastapi import APIRouter, Depends, Cookie, Header, HTTPException

from app.core.security import oauth2_scheme
from app.services.user_service import fake_decode_token

router = APIRouter()


# Create a get_current_user dependency
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user


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
