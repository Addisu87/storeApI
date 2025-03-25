import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from datetime import timedelta

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
)
from app.main import app
from app.models.user_models import User
from app.core.deps import get_db
from app.tests.helpers import create_random_item


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
    """Create a fresh database session for a test."""
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture(name="client")
def client_fixture(engine):
    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="superuser")
def superuser_fixture(session: Session):
    user = User(
        email="superuser@example.com",
        hashed_password=get_password_hash("supersecret"),
        is_superuser=True,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="normal_user")
def normal_user_fixture(session: Session):
    user = User(
        email="user@example.com",
        hashed_password=get_password_hash("usersecret"),
        is_superuser=False,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="superuser_token_headers")
def superuser_token_headers_fixture(client: TestClient, superuser: User):
    login_data = {"username": superuser.email, "password": "supersecret"}
    response = client.post("/api/v1/auth/login", data=login_data)
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(name="normal_user_token_headers")
def normal_user_token_headers_fixture(client: TestClient, normal_user: User):
    login_data = {"username": normal_user.email, "password": "usersecret"}
    response = client.post("/api/v1/auth/login", data=login_data)
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


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
