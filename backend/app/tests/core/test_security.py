# app/tests/core/test_security.py
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from jwt import PyJWTError as JWTError
from sqlmodel import Session

from app.core.config import settings
from app.core.security import (
    access_token_expire_minutes,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.schemas import UserCreate
from app.services.user_services import create_user
from app.tests.helpers import random_email, random_lower_string


def test_create_access_token(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)
    db.commit()

    access_token = create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=access_token_expire_minutes()),
    )
    assert access_token


def test_verify_password() -> None:
    password = random_lower_string()
    hashed_password = get_password_hash(password)

    assert verify_password(password, hashed_password) is True
    assert verify_password("wrongpassword", hashed_password) is False


def test_get_password_hash() -> None:
    password = random_lower_string()
    hashed_password = get_password_hash(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password) is True


def test_invalid_token() -> None:
    invalid_token = "invalidtoken"
    with pytest.raises(JWTError):
        jwt.decode(invalid_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_expired_token(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)
    db.commit()

    access_token = create_access_token(
        subject=user.email, expires_delta=timedelta(seconds=-1)
    )
    with pytest.raises(JWTError):
        jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_valid_token(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)
    db.commit()

    access_token = create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=access_token_expire_minutes()),
    )
    payload = jwt.decode(
        access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == user.email


def test_create_access_token_with_custom_expiration(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)
    db.commit()

    custom_expiration = timedelta(hours=1)
    access_token = create_access_token(
        subject=user.email, expires_delta=custom_expiration
    )
    payload = jwt.decode(
        access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    expire_time = datetime.fromtimestamp(payload["exp"], timezone.utc)
    assert expire_time > datetime.now(timezone.utc)


def test_create_access_token_with_invalid_secret_key(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)
    db.commit()

    access_token = create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=access_token_expire_minutes()),
    )
    with pytest.raises(JWTError):
        jwt.decode(access_token, "invalidsecretkey", algorithms=[settings.ALGORITHM])


def test_create_access_token_with_invalid_algorithm(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)
    db.commit()

    access_token = create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=access_token_expire_minutes()),
    )
    with pytest.raises(JWTError):
        jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS512"])
