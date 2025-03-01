from sqlmodel import Session

from app.models.schemas import UserCreate
from app.services.user_services import authenticate_user, create_user
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
