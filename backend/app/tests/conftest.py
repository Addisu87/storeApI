from typing import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.main import app
from app.models.schemas import User
from app.tests.helpers import create_random_item

ALEMBIC_INI_PATH = "alembic.ini"


@pytest.fixture(name="engine", scope="session")
def engine_fixture() -> Generator[Engine, None, None]:
    test_settings = get_settings("test")
    test_engine = create_engine(test_settings.get_db_uri_string(), echo=True)

    alembic_cfg = Config(ALEMBIC_INI_PATH)
    alembic_cfg.set_main_option("sqlalchemy.url", test_settings.get_db_uri_string())
    try:
        command.upgrade(alembic_cfg, "head")
        print("Alembic migrations applied successfully")
    except Exception as e:
        print(f"Failed to apply Alembic migrations: {e}")
        raise

    yield test_engine


@pytest.fixture(name="db", scope="function")
def db_fixture(engine: Engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(name="client", scope="module")
def client_fixture() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_settings] = lambda: get_settings("test")
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def superuser(db: Session) -> User:
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


@pytest.fixture(scope="function")
def normal_user(db: Session) -> User:
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


@pytest.fixture(scope="function")
def superuser_token_headers(
    client: TestClient, superuser: User, db: Session
) -> dict[str, str]:
    data = {"username": "superuser@example.com", "password": "supersecret"}
    r = client.post(f"{get_settings('test').API_V1_STR}/login/access-token", data=data)
    assert r.status_code == 200, f"Superuser login failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="function")
def normal_user_token_headers(
    client: TestClient, normal_user: User, db: Session
) -> dict[str, str]:
    data = {"username": "user@example.com", "password": "usersecret"}
    r = client.post(f"{get_settings('test').API_V1_STR}/login/access-token", data=data)
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
