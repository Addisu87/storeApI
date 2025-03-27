from datetime import datetime, timedelta, timezone

import jwt
import pytest
from jwt import PyJWTError as JWTError
from sqlmodel import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user_models import UserCreate
from app.services.user_services import create_user
from app.tests.helpers import random_email, random_lower_string
from app.utilities.constants import access_token_expire_minutes


def test_create_access_token(session: Session) -> None:
    """Test creating an access token."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=session, user_create=user_in)
    session.commit()

    access_token = create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=access_token_expire_minutes()),
    )
    assert access_token
    # Verify token can be decoded
    payload = jwt.decode(
        access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == user.email


def test_verify_password() -> None:
    """Test password verification."""
    password = random_lower_string()
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)


def test_get_password_hash() -> None:
    """Test password hashing."""
    password = random_lower_string()
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert verify_password(password, hashed_password) is True


def test_invalid_token() -> None:
    """Test handling of invalid token format."""
    invalid_token = "invalidtoken"
    with pytest.raises(JWTError):
        jwt.decode(invalid_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_expired_token(session: Session) -> None:
    """Test handling of expired tokens."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=session, user_create=user_in)
    session.commit()

    # Create token that's already expired
    access_token = create_access_token(
        subject=user.email, expires_delta=timedelta(minutes=-1)
    )
    with pytest.raises(JWTError):
        jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_valid_token(session: Session) -> None:
    """Test validation of a valid token."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=session, user_create=user_in)
    session.commit()

    access_token = create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=access_token_expire_minutes()),
    )
    payload = jwt.decode(
        access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == user.email


def test_create_access_token_with_custom_expiration(session: Session) -> None:
    """Test token creation with custom expiration time."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=session, user_create=user_in)
    session.commit()

    custom_expiration = timedelta(hours=1)
    access_token = create_access_token(
        subject=user.email, expires_delta=custom_expiration
    )
    payload = jwt.decode(
        access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    expire_time = datetime.fromtimestamp(payload["exp"], timezone.utc)
    assert expire_time > datetime.now(timezone.utc)
    # Verify expiration is within expected range
    expected_expiration = datetime.now(timezone.utc) + custom_expiration
    assert (
        abs((expire_time - expected_expiration).total_seconds()) < 5
    )  # Allow 5 seconds difference


def test_create_access_token_with_invalid_secret_key(session: Session) -> None:
    """Test token validation with incorrect secret key."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=session, user_create=user_in)
    session.commit()

    access_token = create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=access_token_expire_minutes()),
    )
    with pytest.raises(JWTError):
        jwt.decode(access_token, "invalidsecretkey", algorithms=[settings.ALGORITHM])


def test_create_access_token_with_invalid_algorithm(session: Session) -> None:
    """Test token validation with incorrect algorithm."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=session, user_create=user_in)
    session.commit()

    access_token = create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=access_token_expire_minutes()),
    )
    with pytest.raises(JWTError):
        jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS512"])
