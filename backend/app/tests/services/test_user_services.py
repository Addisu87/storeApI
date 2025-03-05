# app/tests/services/test_user_services.py
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app.core.security import verify_password
from app.models.schemas import User, UserCreate, UserUpdate
from app.services.user_services import authenticate_user, create_user, update_user
from app.tests.helpers import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)

    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)

    auth_user = authenticate_user(session=db, email=email, password=password)
    assert auth_user
    assert user.email == auth_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = authenticate_user(session=db, email=email, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)

    assert user.is_active is True


def test_check_if_user_is_inactive(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_active=False)
    user = create_user(session=db, user_create=user_in)

    assert user.is_active is False


def test_check_if_user_is_superuser(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = create_user(session=db, user_create=user_in)

    assert user.is_superuser is True


def test_check_if_user_is_normal_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        email=email,
        password=password,
    )
    user = create_user(session=db, user_create=user_in)

    assert user.is_superuser is False


def test_update_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    new_password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = create_user(session=db, user_create=user_in)
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    if user.id is not None:
        update_user(session=db, db_user=user, user_in=user_in_update)
    new_user = db.get(User, user.id)

    assert new_user
    assert user.email == new_user.email
    assert verify_password(new_password, new_user.hashed_password)


def test_get_user(db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password, is_superuser=True)
    user = create_user(session=db, user_create=user_in)

    new_user = db.get(User, user.id)

    assert new_user
    assert user.email == new_user.email
    assert jsonable_encoder(user) == jsonable_encoder(new_user)
