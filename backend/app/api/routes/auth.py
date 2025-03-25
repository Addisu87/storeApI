# app/api/routes/auth.py

from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import CurrentUser, SessionDep
from app.core.security import (
    access_token_expire_minutes,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.auth_models import NewPassword, Token
from app.models.generic_models import Message
from app.models.user_models import UserCreate, UserPublic, UserRegister
from app.services.email_services import generate_reset_password_email, send_email
from app.services.password_services import verify_password_reset_token
from app.services.user_services import create_user, get_user_by_email
from app.utilities.constants import email_reset_token_expire_hours

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def register_user(*, session: SessionDep, user_in: UserRegister) -> Any:
    """Register new user."""
    # Check if user exists using direct query
    existing_user = get_user_by_email(session=session, email=user_in.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user_create = UserCreate(
        email=user_in.email,
        password=user_in.password,
        is_active=True,
    )
    user = create_user(session=session, user_create=user_create)
    session.refresh(user)
    return user


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = get_user_by_email(session=session, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    access_token_expires = timedelta(minutes=access_token_expire_minutes())
    return Token(
        access_token=create_access_token(
            subject=user.email,
            expires_delta=access_token_expires,
        ),
        token_type="bearer",
    )


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """Test access token."""
    return current_user


@router.post("/password-recovery/{email}", response_model=Message)
async def recover_password(
    email: str,
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> Any:
    """Password Recovery"""
    user = get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )

    password_reset_token = create_access_token(
        subject=email,
        expires_delta=timedelta(hours=email_reset_token_expire_hours()),
    )
    email_data = generate_reset_password_email(
        email_to=email,
        email=email,
        token=password_reset_token,
    )
    await send_email(
        email_to=email,
        email_data=email_data,
        background_tasks=background_tasks,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password", response_model=Message)
def reset_password(session: SessionDep, body: NewPassword) -> Any:
    """Reset password"""
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    user.hashed_password = get_password_hash(body.new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return Message(message="Password updated successfully")
