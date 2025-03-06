# Authentication/authorization dependencies
# Reusable components for security in routes.
# dependencies injection/resources/providers/services/injectables/components
# Have shared logic (the same code logic again and again).
# Share database connections.
# Enforce security, authentication, role requirements, etc.
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, create_engine

from app.core.config import settings
from app.models.auth_models import TokenPayload
from app.models.user_models import User

# Declaring OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token",
)

# Create a synchronous database engine
engine = create_engine(settings.get_db_uri_string(), echo=True)


def get_db() -> Generator[Session, None, None]:
    """Provide a synchronous database session."""
    with Session(engine) as session:
        yield session


# Use Annotated for Dependency Injection
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


# Create a get_current_user dependency
async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Retrieve the current user from the database."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = session.get(User, token_data.sub)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user


CurrentUser = Annotated[User, Security(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Retrieve the current active superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
