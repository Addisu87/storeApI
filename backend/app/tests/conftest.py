from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings
from app.core.deps import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.main import app
from app.models.user_models import User


# Test database setup
@pytest.fixture(name="engine")
def engine_fixture():
    test_settings = get_settings("test")
    engine = create_engine(
        test_settings.get_db_uri_string(),
        echo=True,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(engine):
    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="superuser")
def superuser_fixture(session):
    user = User(
        email="admin@test.com",
        hashed_password=get_password_hash("supersecret"),
        is_superuser=True,
        is_active=True,
        full_name="Super User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="normal_user")
def normal_user_fixture(session):
    user = User(
        email="user@test.com",
        hashed_password=get_password_hash("usersecret"),
        is_superuser=False,
        is_active=True,
        full_name="Normal User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="other_user")
def other_user_fixture(session: Session) -> User:
    user = User(
        email="other@example.com",
        hashed_password=get_password_hash("othersecret"),
        is_superuser=False,
        is_active=True,
        full_name="Other User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="superuser_token_headers")
def superuser_token_headers_fixture(superuser: User) -> dict[str, str]:
    access_token = create_access_token(
        subject=superuser.email,  # Use email instead of ID
        expires_delta=timedelta(minutes=30),
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(name="normal_user_token_headers")
def normal_user_token_headers_fixture(normal_user: User) -> dict[str, str]:
    access_token = create_access_token(
        subject=normal_user.email,  # Use email instead of ID
        expires_delta=timedelta(minutes=30),
    )
    return {"Authorization": f"Bearer {access_token}"}


def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_access_token_creation():
    subject = "test@example.com"
    expires_delta = timedelta(minutes=15)

    token = create_access_token(subject, expires_delta)
    assert token
    assert isinstance(token, str)


def test_access_token_expiration():
    subject = "test@example.com"
    expires_delta = timedelta(minutes=-1)  # Already expired

    token = create_access_token(subject, expires_delta)
    assert token


@pytest.fixture
def mock_email_send():
    """Mock the email sending functionality."""
    # Mock both FastMail initialization and send_message
    with patch("fastapi_mail.FastMail.send_message", new_callable=AsyncMock) as mock:
        yield mock
