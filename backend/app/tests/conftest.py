from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, delete

from app.core.security import get_password_hash
from app.database.db import init_db
from app.main import app
from app.models.schemas import Item, User
from app.tests.helpers import (
    create_random_item,
    create_random_user,
    normal_user_token_headers,
    override_current_user,
    superuser_token_headers,
)


# Engine fixture remains the same
@pytest.fixture(name="engine", scope="session")
def engine_fixture() -> Generator[Engine, None, None]:
    test_db_url = "postgresql+psycopg://storeapi:storeapi87@localhost/testdb"
    test_engine = create_engine(test_db_url, echo=False)
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)


# Simplified db fixture to match working example
@pytest.fixture(name="db", scope="session", autouse=True)
def db_fixture(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        session.exec(delete(Item))  # type: ignore
        session.exec(delete(User))  # type: ignore
        session.commit()


# Simplified client fixture
@pytest.fixture(name="client", scope="module")
def client_fixture() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


# Keep your user fixtures but simplify their usage
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
    return user


# Simplify token headers fixtures
@pytest.fixture(name="superuser_token_headers", scope="module")
def superuser_token_headers_fixture(client: TestClient, db: Session) -> dict[str, str]:
    return superuser_token_headers(client)


@pytest.fixture(name="normal_user_token_headers", scope="module")
def normal_user_token_headers_fixture(
    client: TestClient, db: Session
) -> dict[str, str]:
    return normal_user_token_headers(client, db)


# Keep your helper fixtures
@pytest.fixture(name="create_random_user", scope="module")
def create_random_user_fixture(db: Session):
    return lambda: create_random_user(db)


@pytest.fixture(name="create_random_item", scope="module")
def create_random_item_fixture(db: Session):
    return lambda owner=None: create_random_item(db, owner)


@pytest.fixture(name="override_current_user", scope="module")
def override_current_user_fixture():
    return override_current_user
