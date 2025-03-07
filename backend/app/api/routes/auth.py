# app/api/routes/auth.py

import logging
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, status

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
from app.services.password_services import verify_password_reset_token
from app.services.user_services import create_user, get_user_by_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["auth"])


@router.post("/register", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    existing_user = get_user_by_email(session=session, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists!",
        )
    user_create = UserCreate.model_validate(user_in)
    user = create_user(session=session, user_create=user_create)
    session.commit()
    logger.debug(f"New user registered: {user.email}")
    return user


@router.post("/login/access-token", response_model=Token)
def login_access_token(login_data: UserRegister, session: SessionDep) -> Token:
    user = get_user_by_email(session=session, email=login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
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
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """Test access token."""
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(session: SessionDep, email: str) -> Any:
    """Password recovery endpoint."""
    # TODO: Implement password recovery logic
    pass


@router.post("/reset-password")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="A user with this email does not exist in the system!",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    user.hashed_password = get_password_hash(body.new_password)
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully.")


@router.post("/password-recovery-html-content/{email}")
def recover_password_html_content(session: SessionDep, email: str) -> Any:
    """HTML content for password recovery."""
    # TODO: Implement HTML content generation for password recovery
    pass
