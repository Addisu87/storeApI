import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlmodel import func, select

from app.core.config import settings
from app.core.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_current_user,
)
from app.core.security import get_password_hash, verify_password
from app.models.auth_models import UpdatePassword
from app.models.generic_models import Message
from app.models.user_models import (
    User,
    UserCreate,
    UserPublic,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.services.email_services import generate_new_account_email, send_email
from app.services.user_services import create_user, get_user_by_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_STR}/users", tags=["users"])


# CREATE OPERATIONS
@router.post(
    "/",  # This will be mounted at /api/v1/users/
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_user_route(
    session: SessionDep,
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
) -> UserPublic:
    """Create a new user."""
    if get_user_by_email(session=session, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists!",
        )

    user = create_user(session=session, user_create=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        await send_email(
            email_to=user_in.email,
            email_data=email_data,
            background_tasks=background_tasks,
        )
    return UserPublic.model_validate(user)


# READ OPERATIONS
@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: CurrentUser) -> UserPublic:
    """Get current user."""
    return UserPublic.model_validate(current_user)


@router.get("/", response_model=UsersPublic)
async def read_users(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    offset: int = 0,
    limit: int = Query(default=100, le=100),
) -> UsersPublic:
    """Retrieve users."""
    statement = select(User).offset(offset).limit(limit)
    users = session.exec(statement).all()
    total = session.exec(select(func.count()).select_from(User)).first()
    return UsersPublic(
        data=[UserPublic.model_validate(user) for user in users], count=total or 0
    )


# UPDATE OPERATIONS
@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    session: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdateMe,
) -> UserPublic:
    """Update own user details."""
    if user_in.email and user_in.email != current_user.email:
        if get_user_by_email(session=session, email=user_in.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

    if user_in.model_dump(exclude_unset=True):  # Only update if there's data
        current_user.sqlmodel_update(user_in.model_dump(exclude_unset=True))
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
    return UserPublic.model_validate(current_user)


@router.patch("/me/password", response_model=Message)
async def update_user_me_password(
    session: SessionDep,
    current_user: CurrentUser,
    password_data: UpdatePassword,
) -> Message:
    """Update own password."""
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    current_user.hashed_password = get_password_hash(password_data.new_password)
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_user(
    user_id: uuid.UUID,
    session: SessionDep,
    user_in: UserUpdate,
) -> UserPublic:
    """Update a user by ID (superuser only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_in.email and user_in.email != user.email:
        if get_user_by_email(session=session, email=user_in.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

    # Fix: Update user directly instead of calling a non-existent function
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    user.sqlmodel_update(update_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserPublic.model_validate(user)


# DELETE OPERATIONS
@router.delete("/me", response_model=Message)
async def delete_user_me(
    session: SessionDep,
    current_user: CurrentUser,
) -> Message:
    """Delete own user."""
    if current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser cannot be deleted through this endpoint",
        )

    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")
