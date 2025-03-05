# app/api/routes/auth.py

import logging
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.deps import CurrentUser, SessionDep, get_db
from app.core.security import (
    access_token_expire_minutes,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.schemas import (
    Message,
    NewPassword,
    Token,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
)
from app.services.password_services import verify_password_reset_token
from app.services.user_services import create_user, get_user_by_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["auth"])


@router.post("/register", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """Create a new user without the need to be logged in."""
    if get_user_by_email(session=session, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists!",
        )

    user_create = UserCreate.model_validate(user_in)
    user = create_user(session=session, user_create=user_create)
    logger.debug(f"New user registered: {user.email}")
    return user


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """
    OAuth2-compatible token login.
    Authenticate the user and return an access token for future requests.
    """
    # Fetch the user from the database
    user = db.exec(select(User).where(User.email == form_data.username)).first()

    # Verify the user's credentials
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if the user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    # Generate an access token
    access_token_expires = timedelta(minutes=access_token_expire_minutes())
    access_token = create_access_token(
        subject=str(user.id),  # Ensure subject is a string
        expires_delta=access_token_expires,
    )

    # Return the access token
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
    """Reset password using a valid token."""
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )

    user = get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A user with this email does not exist in the system!",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    user.hashed_password = get_password_hash(password=body.new_password)
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully.")


@router.post("/password-recovery-html-content/{email}")
def recover_password_html_content(session: SessionDep, email: str) -> Any:
    """HTML content for password recovery."""
    # TODO: Implement HTML content generation for password recovery
    pass
