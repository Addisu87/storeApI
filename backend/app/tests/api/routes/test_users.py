import uuid
from unittest.mock import patch

from app.core.config import settings
from app.core.deps import get_current_active_superuser
from app.main import app
from app.models.schemas import Item, User
from fastapi.testclient import TestClient
from sqlmodel import Session


# USER CRUD TESTS
# Create User
def test_create_user_success(
    client: TestClient, superuser: User, db: Session, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    with patch("app.services.email_services.send_email") as mock_send_email:
        response = client.post(
            f"{settings.API_V1_STR}/users/",
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
    client: TestClient, superuser: User, normal_user: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        json={"email": "user@example.com", "password": "newpass123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "The user with this email already exists!"


# Read User
def test_read_users_basic(
    client: TestClient, superuser: User, normal_user: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.get(f"{settings.API_V1_STR}/users/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 2
    assert len(data["data"]) >= 2


def test_read_users_pagination(
    client: TestClient, superuser: User, db: Session, override_current_user
):
    for i in range(5):
        db.add(
            User(
                email=f"user{i}@example.com",
                hashed_password="hashed_testpass",  # Simplified for test
                is_superuser=False,
                is_active=True,
            )
        )
    db.commit()

    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.get(f"{settings.API_V1_STR}/users/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 7
    assert len(data["data"]) == 2


def test_read_user_me(client: TestClient, normal_user: User, override_current_user):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


def test_read_user_by_id_self(
    client: TestClient, normal_user: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.get(f"{settings.API_V1_STR}/users/{normal_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


def test_read_user_by_id_superuser(
    client: TestClient, superuser: User, normal_user: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.get(f"{settings.API_V1_STR}/users/{normal_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"


def test_read_user_by_id_forbidden(
    client: TestClient, normal_user: User, db: Session, override_current_user
):
    other_user = User(
        email="other@example.com",
        hashed_password="hashed_otherpass",  # Simplified for test
        is_superuser=False,
        is_active=True,
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.get(f"{settings.API_V1_STR}/users/{other_user.id}")
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient privileges"


# Update User
def test_update_user_me_success(
    client: TestClient, normal_user: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch(
        f"{settings.API_V1_STR}/users/me", json={"full_name": "Updated User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated User"


def test_update_user_me_email_conflict(
    client: TestClient, normal_user: User, superuser: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch(
        f"{settings.API_V1_STR}/users/me", json={"email": "superuser@example.com"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"


def test_update_password_me_success(
    client: TestClient, normal_user: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        json={"current_password": "usersecret", "new_password": "newsecret123"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"


def test_update_password_me_wrong_current(
    client: TestClient, normal_user: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        json={"current_password": "wrongpass", "new_password": "newsecret123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect password"


def test_update_password_me_same_password(
    client: TestClient, normal_user: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        json={"current_password": "usersecret", "new_password": "usersecret"},
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "New password cannot be the same as the current one"
    )


def test_update_user_success(
    client: TestClient, superuser: User, normal_user: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.patch(
        f"{settings.API_V1_STR}/users/{normal_user.id}",
        json={"full_name": "Updated Normal User", "password": "newpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Normal User"


def test_update_user_not_found(
    client: TestClient, superuser: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    nonexistent_id = uuid.uuid4()
    response = client.patch(
        f"{settings.API_V1_STR}/users/{nonexistent_id}",
        json={"full_name": "Nonexistent"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# Delete User
def test_delete_user_me_normal(
    client: TestClient, normal_user: User, db: Session, override_current_user
):
    item = Item(title="Test Item", description="Test", owner_id=normal_user.id)
    db.add(item)
    db.commit()

    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.delete(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"
    assert db.get(Item, item.id) is None


def test_delete_user_me_superuser(
    client: TestClient, superuser: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.delete(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 403
    assert response.json()["detail"] == "Superusers cannot delete themselves"


def test_delete_user_success(
    client: TestClient,
    superuser: User,
    normal_user: User,
    db: Session,
    override_current_user,
):
    item = Item(title="Test Item", description="Test", owner_id=normal_user.id)
    db.add(item)
    db.commit()

    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.delete(f"{settings.API_V1_STR}/users/{normal_user.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"
    assert db.get(Item, item.id) is None


def test_delete_user_self_forbidden(
    client: TestClient, superuser: User, override_current_user
):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        superuser
    )
    response = client.delete(f"{settings.API_V1_STR}/users/{superuser.id}")
    assert response.status_code == 403
    assert response.json()["detail"] == "Superusers cannot delete themselves"
