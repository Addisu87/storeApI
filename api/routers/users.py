from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from typing import Annotated

from api.dependencies import CommonQueryParams


router = APIRouter(prefix="", tags=["users"])


# Base user
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


# Input model- Inheritance
class UserIn(UserBase):
    password: str


# Output model
class UserOut(UserBase):
    pass


# Database model - have a hashed password
class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db


# Don't do this in production!
@router.post("/users/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved


@router.get("/users/", tags=["users"])
async def read_users(commons: CommonQueryParams):
    return commons


# @router.get("/users/me", tags=["users"])
# async def read_user_me():
#     return {"username": "fakecurrentuser"}


# @router.get("/users/{user_id}", tags=["users"])
# async def read_user(user_id: int):
#     return {"user_id": user_id}
