# app/tests/conftest.py
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.main import app
from app.models.schemas import User
from app.tests.helpers import create_random_item

# Use existing storeapidb
TEST_DB_URL = "postgresql+psycopg://storeapi:storeapi87@localhost:5432/storeapidb"


@pytest.fixture(name="engine", scope="session")
def engine_fixture() -> Generator[Engine, None, None]:
    test_engine = create_engine(TEST_DB_URL, echo=True)  # Enable echo for debugging
    yield test_engine


@pytest.fixture(name="db", scope="function")
def db_fixture(engine: Engine) -> Generator[Session, None, None]:
    """Provide a fresh session per test with rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    SQLModel.metadata.create_all(bind=connection)  # Ensure tables exist
    yield session
    session.close()
    transaction.rollback()  # Roll back changes per test
    connection.close()


@pytest.fixture(name="client", scope="module")
def client_fixture() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_settings] = lambda: get_settings("test")
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def superuser(db: Session) -> User:
    """Create a superuser per test."""
    existing = db.exec(
        select(User).where(User.email == "superuser@example.com")
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
    user = User(
        email="superuser@example.com",
        hashed_password=get_password_hash("supersecret"),
        is_superuser=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Superuser created: {user.email}, ID: {user.id}")
    return user


@pytest.fixture(scope="function")
def normal_user(db: Session) -> User:
    """Create a normal user per test."""
    existing = db.exec(select(User).where(User.email == "user@example.com")).first()
    if existing:
        db.delete(existing)
        db.commit()
    user = User(
        email="user@example.com",
        hashed_password=get_password_hash("usersecret"),
        is_superuser=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Normal user created: {user.email}, ID: {user.id}")
    return user


@pytest.fixture(scope="function")
def superuser_token_headers(
    client: TestClient, superuser: User, db: Session
) -> dict[str, str]:
    """Generate superuser token per test with explicit DB check."""
    # Ensure the user is in the DB before login
    db_user = db.exec(select(User).where(User.email == "superuser@example.com")).first()
    print(f"Superuser in DB before login: {db_user.email if db_user else 'Not found'}")

    data = {"username": "superuser@example.com", "password": "supersecret"}
    r = client.post(f"{get_settings('test').API_V1_STR}/login/access-token", data=data)
    print(f"Superuser login response status: {r.status_code}, body: {r.text}")
    assert r.status_code == 200, f"Superuser login failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="function")
def normal_user_token_headers(
    client: TestClient, normal_user: User, db: Session
) -> dict[str, str]:
    """Generate normal user token per test with explicit DB check."""
    # Ensure the user is in the DB before login
    db_user = db.exec(select(User).where(User.email == "user@example.com")).first()
    print(
        f"Normal user in DB before login: {db_user.email if db_user else 'Not found'}"
    )

    data = {"username": "user@example.com", "password": "usersecret"}
    r = client.post(f"{get_settings('test').API_V1_STR}/login/access-token", data=data)
    print(f"Normal user login response status: {r.status_code}, body: {r.text}")
    assert r.status_code == 200, f"Normal user login failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="function")
def create_random_user(db: Session):
    return lambda: create_random_user(db)


@pytest.fixture(scope="function")
def create_random_item_fixture(db: Session):
    return lambda owner=None: create_random_item(db=db, owner=owner)


@pytest.fixture(scope="function")
def override_current_user():
    return override_current_user
