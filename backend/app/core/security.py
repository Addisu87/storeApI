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


# Create access token
def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """Create access token

    Args:
        subject (str | Any): _description_
        expires_delta (timedelta): _description_

    Returns:
        str: encoded_jwt
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Password hashing - Converting into a sequence of bytes(strings)
# it looks like gibberish


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
