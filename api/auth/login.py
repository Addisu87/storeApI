from typing import Annotated
from fastapi import APIRouter, Form

router = APIRouter(prefix="", tags=["auth"])


@router.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}
