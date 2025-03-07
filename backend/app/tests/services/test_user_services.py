# app/tests/services/test_user_services.py
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app.core.security import verify_password
from app.models.user_models import User, UserCreate, UserUpdate
from app.services.user_services import authenticate_user, create_user, update_user
from app.tests.helpers import create_random_user, random_email, random_lower_string


def test_create_user(db: Session) -> None:
    """Test basic user creation with default attributes."""
    user = create_random_user(db)
    assert user.email
    assert hasattr(user, "hashed_password")
    assert user.is_active is True
    assert user.is_superuser is False


def test_authenticate_user(db: Session) -> None:
    """Test successful user authentication."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)
    auth_user = authenticate_user(session=db, email=email, password=password)
    assert auth_user
    assert auth_user.email == user.email


def test_not_authenticate_user(db: Session) -> None:
    """Test authentication failure with non-existent user."""
    email = random_email()
    password = random_lower_string()
    user = authenticate_user(session=db, email=email, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    """Test that a user is active by default or when explicitly set."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_active=True)
    user = create_user(session=db, user_create=user_in)
    assert user.is_active is True


def test_check_if_user_is_inactive(db: Session) -> None:
    """Test that a user can be created as inactive."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_active=False)
    user = create_user(session=db, user_create=user_in)
    assert user.is_active is False


def test_check_if_user_is_superuser(db: Session) -> None:
    """Test that a user can be created as a superuser."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = create_user(session=db, user_create=user_in)
    assert user.is_superuser is True


def test_check_if_user_is_normal_user(db: Session) -> None:
    """Test that a user is not a superuser by default or when explicitly set."""
    user = create_random_user(db)  # Uses default is_superuser=False
    assert user.is_superuser is False


def test_update_user(db: Session) -> None:
    """Test updating a user's password and attributes."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = create_user(session=db, user_create=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    updated_user = update_user(session=db, db_user=user, user_in=user_in_update)

    assert updated_user
    assert updated_user.email == user.email
    assert verify_password(new_password, updated_user.hashed_password)
    assert updated_user.is_superuser is True


def test_get_user(db: Session) -> None:
    """Test retrieving a user by ID."""
    user = create_random_user(db)
    fetched_user = db.get(User, user.id)

    assert fetched_user
    assert fetched_user.email == user.email
    assert jsonable_encoder(fetched_user) == jsonable_encoder(user)
