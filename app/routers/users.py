# Routes for user operations
from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.common_query import CommonQueryParams
from app.schemas.users import User
from app.core.dependencies import get_current_active_user


router = APIRouter(prefix="", tags=["users"])


@router.get("/users/", tags=["users"])
async def read_users(commons: Annotated[dict, Depends(CommonQueryParams)]):
    """
    Fetch users based on common query parameters.
    """
    return commons


# Inject the current user - get the user


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


# @router.get("/users/{user_id}", tags=["users"])
# async def read_user(user_id: int):
#     return {"user_id": user_id}
