from fastapi import APIRouter, Depends

from app.dependencies.common_query import CommonQueryParams
from app.services.user_service import fake_save_user
from app.schemas.users import UserIn, UserOut


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
async def read_users(commons: CommonQueryParams = Depends()):
    """
    Fetch users based on common query parameters.
    """
    return commons


# @router.get("/users/me", tags=["users"])
# async def read_user_me():
#     return {"username": "fakecurrentuser"}


# @router.get("/users/{user_id}", tags=["users"])
# async def read_user(user_id: int):
#     return {"user_id": user_id}
