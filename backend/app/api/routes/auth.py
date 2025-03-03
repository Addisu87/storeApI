# Routes for login, token refresh, logout

import logging
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

# Security
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import CurrentUser, SessionDep
from app.core.security import (
    access_token_expire_minutes,
    create_access_token,
    get_password_hash,
)
from app.models.schemas import (
    Message,
    NewPassword,
    Token,
    UserCreate,
    UserPublic,
    UserRegister,
)
from app.services.password_services import verify_password_reset_token
from app.services.user_services import authenticate_user, create_user, get_user_by_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["auth"])


@router.post("/register", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """Create new user without the need to be logged in."""

    user = get_user_by_email(session=session, email=user_in.email)

    logger.debug(user)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists!",
        )
    user_create = UserCreate.model_validate(user_in)
    user = create_user(session=session, user_create=user_create)
    return user


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests."""

    auth_user = authenticate_user(
        session=session, email=form_data.username, password=form_data.password
    )

    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    elif not auth_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    access_token_expires = timedelta(minutes=access_token_expire_minutes())
    access_token = create_access_token(
        auth_user.id,
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """Test access token"""

    return current_user


@router.post("/password-recovery/{email}")
def recover_password(session: SessionDep, email: str) -> Any:
    """Password Recovery"""
    pass


@router.post("/reset-password")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """Reset Password"""

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
            detail="A user with this email does not exit in the system!",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successefully.")


@router.post("/password-reovery-html-content/{email}")
def recover_password_html_content(session: SessionDep, email: str) -> Any:
    """HTML Content for Password Recovery"""
    pass
