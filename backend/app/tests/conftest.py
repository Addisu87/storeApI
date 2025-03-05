# app/tests/conftest.py
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, delete

from app.core.config import settings
from app.core.security import get_password_hash
from app.database.db import init_db
from app.main import app
from app.models.schemas import Item, User
from app.tests.helpers import (
    create_random_item,
    create_random_user,
    override_current_user,
)


@pytest.fixture(name="engine", scope="session")
def engine_fixture() -> Generator[Engine, None, None]:
    test_db_url = "postgresql+psycopg://storeapi:storeapi87@localhost/testdb"
    test_engine = create_engine(test_db_url, echo=True)  # Enable echo for debugging
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="db", scope="session", autouse=True)
def db_fixture(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        session.exec(delete(Item))  # type: ignore
        session.exec(delete(User))  # type: ignore
        session.commit()


@pytest.fixture(name="client", scope="module")
def client_fixture() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


@pytest.fixture(name="superuser", scope="module")
def superuser_fixture(db: Session) -> User:
    user = User(
        email="superuser@example.com",
        hashed_password=get_password_hash("supersecret"),
        is_superuser=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Superuser created: {user.email}, is_active={user.is_active}")
    assert user.is_active, "Superuser should be active"
    return user


@pytest.fixture(name="normal_user", scope="module")
def normal_user_fixture(db: Session) -> User:
    user = User(
        email="user@example.com",
        hashed_password=get_password_hash("usersecret"),
        is_superuser=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Normal user created: {user.email}, is_active={user.is_active}")
    assert user.is_active, "Normal user should be active"
    return user


@pytest.fixture(name="superuser_token_headers", scope="module")
def superuser_token_headers_fixture(
    client: TestClient, superuser: User
) -> dict[str, str]:
    data = {"username": "superuser@example.com", "password": "supersecret"}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    print(f"Superuser login response: {r.text}")
    assert r.status_code == 200, f"Superuser login failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(name="normal_user_token_headers", scope="module")
def normal_user_token_headers_fixture(
    client: TestClient, normal_user: User
) -> dict[str, str]:
    data = {"username": "user@example.com", "password": "usersecret"}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    print(f"Normal user login response: {r.text}")
    assert r.status_code == 200, f"Normal user login failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(name="create_random_user", scope="module")
def create_random_user_fixture(db: Session):
    return lambda: create_random_user(db)


@pytest.fixture(name="create_random_item", scope="module")
def create_random_item_fixture(db: Session):
    return lambda owner=None: create_random_item(db, owner)


@pytest.fixture(name="override_current_user", scope="module")
def override_current_user_fixture():
    return override_current_user
