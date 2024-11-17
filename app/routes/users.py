from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.common_query import CommonQueryParams
from app.schemas.users import UserIn, UserOut
from app.services.user_service import fake_save_user
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="", tags=["users"])


# Don't do this in production!
@router.post("/users/", response_model=UserOut)
async def create_user(user_in: UserIn):
    """
    Create a new user and return the user details without the password.
    """
    user_saved = fake_save_user(user_in)
    return user_saved


@router.get("/users/", tags=["users"])
async def read_users(commons: Annotated[dict, Depends(CommonQueryParams)]):
    """
    Fetch users based on common query parameters.
    """
    return commons


# Inject the current user
@router.get("/users/me", tags=["users"])
async def read_users_me(current_user: Annotated[UserIn, Depends(get_current_user)]):
    return current_user


# @router.get("/users/{user_id}", tags=["users"])
# async def read_user(user_id: int):
#     return {"user_id": user_id}
