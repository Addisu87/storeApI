from app.core.config import settings
from app.models.user_models import User
from app.tests.helpers import random_email, random_lower_string
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import patch


def test_create_user_success(client: TestClient, superuser_token_headers: dict):
    """Test creating a new user."""
    email = random_email()
    password = random_lower_string()
    data = {"email": email, "password": password}

    # Mock the send_email function
    with patch("app.api.routes.users.send_email") as mock_send_email:
        response = client.post(
            f"{settings.API_V1_STR}/users/",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == status.HTTP_201_CREATED
        created_user = response.json()
        assert created_user["email"] == email
        assert "id" in created_user

        # Verify that send_email was called if emails are enabled
        if settings.EMAILS_ENABLED:
            mock_send_email.assert_called_once()
        else:
            mock_send_email.assert_not_called()


def test_read_users(client: TestClient, superuser_token_headers: dict):
    """Test retrieving users list."""
    response = client.get(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert "data" in users
    assert "count" in users
    assert isinstance(users["data"], list)
    assert isinstance(users["count"], int)


def test_read_user_me(client: TestClient, normal_user_token_headers: dict):
    """Test retrieving own user data."""
    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert "email" in user_data
    assert "id" in user_data


def test_delete_user_self_forbidden(
    client: TestClient,
    superuser: User,
    superuser_token_headers: dict,
):
    """Test that superusers cannot delete themselves."""
    response = client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=superuser_token_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        response.json()["detail"] == "Superuser cannot be deleted through this endpoint"
    )
