# Security-related logic (JWT(JSON Web Tokens), OAuth, hashing)
# Security utilities (password hashing, token creation, verification)

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

# Security
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def access_token_expire_minutes() -> int:
    return 60 * 24 * 7


def confirm_token_expire_minutes() -> int:
    return 60 * 24


def email_reset_token_expire_hours() -> int:
    return 48


# Create access token
def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """Create an access token.

    Args:
        subject (str | Any): The subject of the token.
        expires_delta (timedelta): The time delta for token expiration.

    Returns:
        str: The encoded JWT.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=access_token_expire_minutes())
    )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password (str): The plain password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)
