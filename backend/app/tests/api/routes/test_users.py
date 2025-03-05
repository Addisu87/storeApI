# app/tests/api/routes/test_users.py

import uuid
from unittest.mock import patch

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.schemas import Item, User
from fastapi.testclient import TestClient
from sqlmodel import Session

# USER CRUD TESTS ORGANIZED BY CRUD OPERATION


# CREATE TESTS
def test_create_user_success(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
):
    with patch("app.services.email_services.send_email") as mock_send_email:
        response = client.post(
            f"{settings.API_V1_STR}/users/",
            headers=superuser_token_headers,
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
        assert mock_send_email.called is True


def test_create_user_duplicate_email(
    client: TestClient, superuser_token_headers: dict[str, str], normal_user: User
):
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json={"email": "user@example.com", "password": "newpass123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "The user with this email already exists!"


# READ TESTS
def test_read_user_me(client: TestClient, normal_user_token_headers: dict[str, str]):
    response = client.get(
        f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


def test_read_user_by_id_self(
    client: TestClient, normal_user: User, normal_user_token_headers: dict[str, str]
):
    response = client.get(
        f"{settings.API_V1_STR}/users/{normal_user.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


def test_read_user_by_id_superuser(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user: User,
):
    response = client.get(
        f"{settings.API_V1_STR}/users/{normal_user.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


def test_read_user_by_id_forbidden(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
):
    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("otherpass"),
        is_superuser=False,
        is_active=True,
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    response = client.get(
        f"{settings.API_V1_STR}/users/{other_user.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient privileges"


def test_read_users_basic(
    client: TestClient, superuser_token_headers: dict[str, str], normal_user: User
):
    response = client.get(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 2
    assert len(data["data"]) >= 2


def test_read_users_pagination(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
):
    for i in range(5):
        db.add(
            User(
                email=f"user{i}@example.com",
                hashed_password=get_password_hash("testpass"),
                is_superuser=False,
                is_active=True,
            )
        )
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/users/?skip=2&limit=2",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 7  # superuser, normal_user, +5 new users
    assert len(data["data"]) == 2


# UPDATE TESTS
def test_update_user_me_success(
    client: TestClient, normal_user_token_headers: dict[str, str]
):
    response = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json={"full_name": "Updated User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated User"


def test_update_user_me_email_conflict(
    client: TestClient, normal_user_token_headers: dict[str, str], superuser: User
):
    response = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json={"email": "superuser@example.com"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"


def test_update_password_me_success(
    client: TestClient, normal_user_token_headers: dict[str, str]
):
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=normal_user_token_headers,
        json={"current_password": "usersecret", "new_password": "newsecret123"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"


def test_update_password_me_wrong_current(
    client: TestClient, normal_user_token_headers: dict[str, str]
):
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=normal_user_token_headers,
        json={"current_password": "wrongpass", "new_password": "newsecret123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect password"


def test_update_password_me_same_password(
    client: TestClient, normal_user_token_headers: dict[str, str]
):
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=normal_user_token_headers,
        json={"current_password": "usersecret", "new_password": "usersecret"},
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "New password cannot be the same as the current one"
    )


def test_update_user_success(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user: User,
):
    response = client.patch(
        f"{settings.API_V1_STR}/users/{normal_user.id}",
        headers=superuser_token_headers,
        json={"full_name": "Updated Normal User", "password": "newpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Normal User"


def test_update_user_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
):
    nonexistent_id = uuid.uuid4()
    response = client.patch(
        f"{settings.API_V1_STR}/users/{nonexistent_id}",
        headers=superuser_token_headers,
        json={"full_name": "Nonexistent"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# DELETE TESTS
def test_delete_user_me_normal(
    client: TestClient,
    normal_user: User,
    normal_user_token_headers: dict[str, str],
    db: Session,
):
    item = Item(title="Test Item", description="Test", owner_id=normal_user.id)
    db.add(item)
    db.commit()

    response = client.delete(
        f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"
    assert db.get(Item, item.id) is None


def test_delete_user_me_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
):
    response = client.delete(
        f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Superusers cannot delete themselves"


def test_delete_user_success(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user: User,
    db: Session,
):
    item = Item(title="Test Item", description="Test", owner_id=normal_user.id)
    db.add(item)
    db.commit()

    response = client.delete(
        f"{settings.API_V1_STR}/users/{normal_user.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"
    assert db.get(Item, item.id) is None


def test_delete_user_self_forbidden(
    client: TestClient, superuser: User, superuser_token_headers: dict[str, str]
):
    response = client.delete(
        f"{settings.API_V1_STR}/users/{superuser.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Superusers cannot delete themselves"
