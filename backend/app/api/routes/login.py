# Routes for login, token refresh, logout

from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

# Security
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.deps import CurrentUser, SessionDep
from app.core.security import create_access_token
from app.models.schemas import Token, UserPublic
from app.services.user_services import authenticate_user

router = APIRouter(prefix="", tags=["auth"])


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests

    Args:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends()]): The OAuth2 form data containing username and password
        session (SessionDep): Database session dependency

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        Token: _description_
    """
    user = authenticate_user(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user.id,
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """Test access token

    Args:
        current_user (UserPublic): The current user

    Returns:
        UserPublic: The current user
    """

    return current_user
