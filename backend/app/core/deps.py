# Authentication/authorization dependencies
# Reusable components for security in routes.
# dependencies injection/resources/providers/services/injectables/components
# Have shared logic (the same code logic again and again).
# Share database connections.
# Enforce security, authentication, role requirements, etc.

from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Security, status
from fastapi.security import SecurityScopes
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.api.schemas.token import TokenData
from app.api.schemas.users import User
from app.api.services.user_services import get_user
from app.core.db import engine, fake_users_db
from app.core.security import ALGORITHM, SECRET_KEY, oauth2_scheme

router = APIRouter()


# Create a Session Dependency
def get_session():
    with Session(engine) as session:
        yield session


# Use Annotated for Dependency Injection
SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


# Create a get_current_user dependency
async def get_current_user(security_scopes: SecurityScopes, token: TokenDep) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)  # type: ignore
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


CurrentUser = Annotated[User, Security(get_current_user, scopes=["me"])]


async def get_current_active_user(current_user: CurrentUser) -> User:
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


async def get_token_header(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="X-Token header invalid"
        )


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No Jessica token provided"
        )
