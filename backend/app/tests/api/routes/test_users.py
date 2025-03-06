import uuid
from unittest.mock import patch

import pytest
from app.core.deps import get_current_active_superuser
from app.core.security import get_password_hash
from app.main import app
from app.models.schemas import User
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine


# Test database setup
@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "postgresql+psycopg2://testuser:testpass@localhost/testdb",
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
def test_create_user_success(client, superuser):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    with patch("app.services.email_services.send_email") as mock_send_email:
        response = client.post(
            "/users/",
            json={
                "email": "newuser@example.com",
                "password": "newpass123",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert mock_send_email.called


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


def test_update_user_me_success(client, normal_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch("/users/me", json={"full_name": "Updated User"})
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated User"


def test_update_user_me_email_conflict(client, normal_user, superuser):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch("/users/me", json={"email": "superuser@example.com"})
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"


def test_update_password_me_success(client, normal_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch(
        "/users/me/password",
        json={"current_password": "usersecret", "new_password": "newsecret123"},
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
