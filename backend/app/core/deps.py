# Authentication/authorization dependencies
# Reusable components for security in routes.
# dependencies injection/resources/providers/services/injectables/components
# Have shared logic (the same code logic again and again).
# Share database connections.
# Enforce security, authentication, role requirements, etc.
import logging
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.models.auth_models import TokenPayload
from app.models.user_models import User

logger = logging.getLogger(__name__)

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
        logger.debug(f"Attempting to decode token: {token[:10]}...")

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        logger.debug(f"Decoded payload: {payload}")

        token_data = TokenPayload(**payload)
        logger.debug(f"Token data: {token_data}")

        if not token_data.sub:
            logger.error("No subject claim in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        logger.debug(f"Looking up user with email: {token_data.sub}")
        user = session.exec(select(User).where(User.email == token_data.sub)).first()

        if not user:
            logger.error(f"No user found for email: {token_data.sub}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        logger.debug(f"Found user: {user.email}")
        return user

    except InvalidTokenError as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


CurrentUser = Annotated[User, Security(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Retrieve the current active superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
