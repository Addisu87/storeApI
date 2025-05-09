# Security-related logic (JWT(JSON Web Tokens), OAuth, hashing)
# Security utilities (password hashing, token creation, verification)

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

# Security
from passlib.context import CryptContext

from app.core.config import settings
from app.utilities.constants import access_token_expire_minutes

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Create access token
def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """Create an access token."""

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=access_token_expire_minutes())
    )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    logger.debug(
        f"Verifying password: {plain_password} against hash: {hashed_password}"
    )
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    logger.debug(f"Hashing password: {password}")
    return pwd_context.hash(password)
