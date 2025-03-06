from typing import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine, select

from app.core.config import get_settings, settings
from app.core.security import get_password_hash
from app.main import app
from app.models.schemas import User
from app.tests.helpers import create_random_item, create_random_user

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

    # Create persistent users only if they don’t exist
    with Session(test_engine) as session:
        # Check for existing superuser
        superuser = session.exec(
            select(User).where(User.email == "superuser@example.com")
        ).first()
        if not superuser:
            superuser = User(
                email="superuser@example.com",
                hashed_password=get_password_hash("supersecret"),
                is_superuser=True,
                is_active=True,
            )
            session.add(superuser)
            session.commit()
            session.refresh(superuser)
            print(
                f"Persistent superuser created: {superuser.email}, ID: {superuser.id}"
            )
        else:
            print(f"Superuser already exists: {superuser.email}, ID: {superuser.id}")

        # Check for existing normal user
        normal_user = session.exec(
            select(User).where(User.email == "user@example.com")
        ).first()
        if not normal_user:
            normal_user = User(
                email="user@example.com",
                hashed_password=get_password_hash("usersecret"),
                is_superuser=False,
                is_active=True,
            )
            session.add(normal_user)
            session.commit()
            session.refresh(normal_user)
            print(
                f"Persistent normal user created: {normal_user.email}, ID: {normal_user.id}"
            )
        else:
            print(
                f"Normal user already exists: {normal_user.email}, ID: {normal_user.id}"
            )

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
def client_fixture(engine: Engine) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_settings] = lambda: get_settings("test")
    with TestClient(app) as client:
        # Debug: Verify users exist before yielding client
        with Session(engine) as session:
            superuser = session.exec(
                select(User).where(User.email == "superuser@example.com")
            ).first()
            normal_user = session.exec(
                select(User).where(User.email == "user@example.com")
            ).first()
            print(f"Superuser in DB before client yield: {superuser}")
            print(f"Normal user in DB before client yield: {normal_user}")
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def superuser(engine: Engine) -> User:
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == "superuser@example.com")
        ).first()
        if not user:
            raise Exception("Superuser not found in database")
        return user


@pytest.fixture(scope="module")
def normal_user(engine: Engine) -> User:
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == "user@example.com")
        ).first()
        if not user:
            user = User(
                email="user@example.com",
                hashed_password=get_password_hash("usersecret"),  # Hash the password
                is_superuser=False,
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        return user


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient, superuser: User) -> dict[str, str]:
    data = {"username": "superuser@example.com", "password": "supersecret"}
    r = client.post(f"{get_settings('test').API_V1_STR}/login/access-token", data=data)
    print(f"Superuser login response: {r.status_code}, {r.text}")
    assert r.status_code == 200, f"Superuser login failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, normal_user: User) -> dict[str, str]:
    data = {"email": "user@example.com", "password": "usersecret"}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", json=data)
    print(f"Normal user login response: {r.status_code}, {r.text}")
    assert r.status_code == 200, f"Normal user login failed: {r.text}"
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "id": str(normal_user.id)}


@pytest.fixture(scope="function")
def create_random_user_fixture(db: Session):
    return lambda: create_random_user(db)


@pytest.fixture(scope="function")
def create_random_item_fixture(db: Session):
    return lambda owner=None: create_random_item(db=db, owner=owner)


@pytest.fixture(scope="function")
def override_current_user():
    return override_current_user
