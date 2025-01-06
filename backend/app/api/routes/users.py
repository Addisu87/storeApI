# Routes for user operations
from typing import Annotated

from app.api.schemas.users import User
from app.core.deps import get_current_active_user, get_current_user
from fastapi import APIRouter, Depends, Security

router = APIRouter(prefix="", tags=["users"])


@router.get("/users/", tags=["users"])
async def read_users(users: User, response_model=User):
    """
    Fetch users based on common query parameters.
    """
    return users


# Inject the current user - get the user


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/users/me/items")
async def read_own_items(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@router.get("/status/")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok"}


@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    return {"user_id": user_id}
