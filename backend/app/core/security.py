# Security-related logic (JWT(JSON Web Tokens), OAuth, hashing)
# Security utilities (password hashing, token creation, verification)

from datetime import datetime, timedelta, timezone

import jwt

# Security
from passlib.context import CryptContext

from app.core.config import settings

# Token creation
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Password hashing - Converting into a sequence of bytes(strings)
# it looks like gibberish


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
