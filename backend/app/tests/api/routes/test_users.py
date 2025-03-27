from typing import Dict

from app.core.config import settings
from app.models.user_models import User, UserCreate
from app.services.user_services import create_user
from app.tests.helpers import random_email, random_lower_string
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session


def test_create_user(
    client: TestClient,
    superuser_token_headers: Dict[str, str],
    mock_email_send,
) -> None:
    """Test creating a new user as superuser."""
    email = random_email()
    password = random_lower_string()
    data = UserCreate(
        email=email,
        password=password,
        full_name="Test User",
    ).model_dump()

    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_user = response.json()
    assert created_user["email"] == email
    assert "id" in created_user
    assert "password" not in created_user


def test_create_user_existing_email(
    client: TestClient,
    superuser_token_headers: Dict[str, str],
    normal_user: User,
) -> None:
    """Test creating a user with existing email fails."""
    data = UserCreate(
        email=normal_user.email,
        password=random_lower_string(),
    ).model_dump()

    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()


def test_get_users(
    client: TestClient,
    superuser_token_headers: Dict[str, str],
    normal_user: User,
) -> None:
    """Test retrieving users list."""
    response = client.get(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert isinstance(users["data"], list)
    assert users["count"] > 0
    assert any(user["email"] == normal_user.email for user in users["data"])


def test_get_users_pagination(
    client: TestClient,
    superuser_token_headers: Dict[str, str],
    session: Session,
) -> None:
    """Test users list pagination."""
    # Create multiple users
    for _ in range(5):
        user_in = UserCreate(email=random_email(), password=random_lower_string())
        create_user(session=session, user_create=user_in)

    response = client.get(
        f"{settings.API_V1_STR}/users/?offset=0&limit=3",
        headers=superuser_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users["data"]) == 3


def test_get_current_user(
    client: TestClient,
    normal_user: User,
    normal_user_token_headers: Dict[str, str],
) -> None:
    """Test getting current user details."""
    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["email"] == normal_user.email
    assert user_data["id"] == str(normal_user.id)


def test_update_current_user(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
) -> None:
    """Test updating current user details."""
    new_name = "Updated Name"
    response = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json={"full_name": new_name},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == new_name


def test_update_current_user_email(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
) -> None:
    """Test updating current user email."""
    new_email = random_email()
    response = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json={"email": new_email},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == new_email


def test_update_current_user_email_exists(
    client: TestClient,
    normal_user: User,
    other_user: User,
    normal_user_token_headers: Dict[str, str],
) -> None:
    """Test updating to an existing email fails."""
    response = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json={"email": other_user.email},
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_update_password(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
) -> None:
    """Test updating user password."""
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=normal_user_token_headers,
        json={
            "current_password": "usersecret",
            "new_password": "newpassword123",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Password updated successfully"


def test_update_password_incorrect_current(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
) -> None:
    """Test updating password with incorrect current password."""
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=normal_user_token_headers,
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_current_user(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
) -> None:
    """Test deleting current user."""
    response = client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "User deleted successfully"


def test_superuser_cannot_delete_self(
    client: TestClient,
    superuser_token_headers: Dict[str, str],
) -> None:
    """Test superuser cannot delete themselves."""
    response = client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=superuser_token_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
