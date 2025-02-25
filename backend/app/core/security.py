# Security-related logic (JWT(JSON Web Tokens), OAuth, hashing)
# Security utilities (password hashing, token creation, verification)

from datetime import datetime, timedelta, timezone

import jwt

# Security
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# Token creation
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "78be776ce312b676b1365efdc88d8a3ea88ac796592968419970b8f942235e20"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Declaring OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)


# Create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Password hashing - Converting into a sequence of bytes(strings)
# it looks like gibberish


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
