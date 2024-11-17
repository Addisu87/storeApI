from typing import Annotated

from fastapi import APIRouter, Form
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["auth"])


class FormData(BaseModel):
    username: str
    password: str
    model_config = {"extra": "forbid"}


# Use Form to declare form data input parameters
@router.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data
