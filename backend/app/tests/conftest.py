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
from app.models.user_models import User
from app.services.user_services import get_user_by_email
from app.tests.helpers import create_random_item, create_random_user

ALEMBIC_INI_PATH = "alembic.ini"


@pytest.fixture(name="engine", scope="session")
def engine_fixture() -> Generator[Engine, None, None]:
    test_settings = get_settings("test")
    test_engine = create_engine(test_settings.get_db_uri_string(), echo=True)
    alembic_cfg = Config(ALEMBIC_INI_PATH)
    alembic_cfg.set_main_option("sqlalchemy.url", test_settings.get_db_uri_string())
    command.upgrade(alembic_cfg, "head")
    with Session(test_engine) as session:
        superuser = get_user_by_email(session, "superuser@example.com")
        if not superuser:
            superuser = User(
                email="superuser@example.com",
                hashed_password=get_password_hash("supersecret"),
                is_superuser=True,
                is_active=True,
            )
            session.add(superuser)
        normal_user = get_user_by_email(session, "user@example.com")
        if not normal_user:
            normal_user = User(
                email="user@example.com",
                hashed_password=get_password_hash("usersecret"),
                is_superuser=False,
                is_active=True,
            )
            session.add(normal_user)
        session.commit()
        print(f"Users in DB: {session.exec(select(User)).all()}")
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
        user = get_user_by_email(session, "user@example.com")
        if not user:
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
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def create_random_user_fixture(db: Session):
    return lambda: create_random_user(db)


@pytest.fixture(scope="function")
def create_random_item_fixture(db: Session):
    return lambda owner=None: create_random_item(db=db, owner=owner)


@pytest.fixture(scope="function")
def override_current_user():
    return override_current_user
