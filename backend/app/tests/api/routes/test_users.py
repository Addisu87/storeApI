import uuid

import pytest
from app.core.config import get_settings
from app.core.deps import get_current_active_superuser
from app.core.security import get_password_hash
from app.main import app
from app.models.user_models import User
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from fastapi import status

from app.tests.helpers import random_email, random_lower_string
from app.models.user_models import UserCreate, UserUpdate


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
def client_fixture(session):
    def _get_session_override():
        return session

    app.dependency_overrides[_get_session_override] = _get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="superuser")
def superuser_fixture(session):
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
def normal_user_fixture(session):
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


# Mock current user dependency
def override_current_user(user):
    def _override():
        return user

    return _override


# Tests
def test_create_user_success(
    client: TestClient, superuser_token_headers: dict[str, str]
):
    email = f"test-{uuid.uuid4()}@example.com"
    password = "TestPass123!"
    response = client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert data["is_active"] is True
    assert data["is_superuser"] is False
    assert data["full_name"] == "Test User"


def test_create_user_duplicate_email(client, superuser, normal_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.post(
        "/users/", json={"email": "user@example.com", "password": "newpass123"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"


def test_read_users(client, superuser, normal_user):
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 2
    assert len(data["data"]) >= 2


def test_read_user_me(client, normal_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.get("/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


def test_update_user_me(client: TestClient, normal_user_token_headers: dict[str, str]):
    response = client.patch(
        "/api/v1/users/me",
        headers=normal_user_token_headers,
        json={"full_name": "Updated Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


def test_update_user_me_email_conflict(client, normal_user, superuser):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch("/users/me", json={"email": "superuser@example.com"})
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"


def test_update_user_me_password(
    client: TestClient, normal_user_token_headers: dict[str, str]
):
    response = client.patch(
        "/api/v1/users/me/password",
        headers=normal_user_token_headers,
        json={"current_password": "usersecret", "new_password": "newpassword123"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"


def test_update_password_me_wrong_current(client, normal_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch(
        "/users/me/password",
        json={"current_password": "wrongpass", "new_password": "newsecret123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect password"


def test_update_password_me_same_password(client, normal_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch(
        "/users/me/password",
        json={"current_password": "usersecret", "new_password": "usersecret"},
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "New password cannot be the same as the current one"
    )


def test_delete_user_me_normal(client, normal_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.delete("/users/me")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"


def test_delete_user_me_superuser(client, superuser):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.delete("/users/me")
    assert response.status_code == 403
    assert response.json()["detail"] == "Superusers cannot delete themselves"


def test_read_user_by_id_self(client, normal_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.get(f"/users/{normal_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


def test_read_user_by_id_superuser(client, superuser, normal_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.get(f"/users/{normal_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


def test_read_user_by_id_forbidden(client, normal_user, session):
    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("otherpass"),
        is_superuser=False,
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.get(f"/users/{other_user.id}")
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient privileges"


def test_update_user_success(client, superuser, normal_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.patch(
        f"/users/{normal_user.id}",
        json={"full_name": "Updated Normal User", "password": "newpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Normal User"


def test_update_user_not_found(client, superuser):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.patch(f"/users/{uuid.uuid4()}", json={"full_name": "Nonexistent"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user_success(client, superuser, normal_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.delete(f"/users/{normal_user.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"


def test_delete_user_self_forbidden(client, superuser):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.delete(f"/users/{superuser.id}")
    assert response.status_code == 403
    assert response.json()["detail"] == "Superusers cannot delete themselves"


def test_create_user(client, superuser_token_headers):
    email = random_email()
    password = random_lower_string()
    data = {"email": email, "password": password}
    
    response = client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json=data
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_user = response.json()
    assert created_user["email"] == email
    assert "id" in created_user


def test_read_users(client, superuser_token_headers):
    response = client.get(
        "/api/v1/users/",
        headers=superuser_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert "data" in users
    assert "count" in users
    assert isinstance(users["data"], list)
    assert users["count"] >= 1


def test_read_user_me(client, normal_user, normal_user_token_headers):
    response = client.get(
        "/api/v1/users/me",
        headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["email"] == normal_user.email
    assert user_data["id"] == str(normal_user.id)


def test_update_user_me(client, normal_user, normal_user_token_headers):
    new_name = random_lower_string()
    response = client.patch(
        "/api/v1/users/me",
        headers=normal_user_token_headers,
        json={"full_name": new_name}
    )
    assert response.status_code == status.HTTP_200_OK
    updated_user = response.json()
    assert updated_user["full_name"] == new_name


@pytest.mark.parametrize(
    "user_data,expected_status",
    [
        ({"email": "invalid"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"password": "short"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
def test_create_user_validation(
    client, 
    superuser_token_headers, 
    user_data, 
    expected_status
):
    response = client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json=user_data
    )
    assert response.status_code == expected_status
