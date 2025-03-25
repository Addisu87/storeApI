from sqlmodel import Session

from app.models.user_models import UserCreate, UserUpdate
from app.services.user_services import (
    create_user,
    get_user,
    get_user_by_email,
    update_user,
)
from app.tests.helpers import random_email, random_lower_string


def test_create_user(session: Session):
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=session, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")
    assert user.hashed_password != password


def test_get_user(session: Session, normal_user):
    user = get_user(session=session, user_id=normal_user.id)
    assert user
    assert user.email == normal_user.email
    assert user.id == normal_user.id


def test_get_user_by_email(session: Session, normal_user):
    user = get_user_by_email(session=session, email=normal_user.email)
    assert user
    assert user.email == normal_user.email
    assert user.id == normal_user.id


def test_update_user(session: Session, normal_user):
    new_name = random_lower_string()
    user_update = UserUpdate(full_name=new_name)
    updated_user = update_user(
        session=session, db_user=normal_user, user_in=user_update
    )
    assert updated_user.id == normal_user.id
    assert updated_user.full_name == new_name
    assert updated_user.email == normal_user.email
