from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from app.core.security import create_access_token, get_password_hash
from app.models.user_models import User
from app.tests.helpers import random_email, random_lower_string
from app.utilities.constants import email_reset_token_expire_hours
from fastapi import status


def test_register_user(client):
    email = random_email()
    password = random_lower_string()
    data = {"email": email, "password": password}
    response = client.post("/api/v1/register", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result["email"] == email
    assert "id" in result


def test_register_existing_user(client, session, normal_user):
    """Test registering a user with an email that already exists."""
    data = {"email": normal_user.email, "password": "newpassword123"}
    response = client.post("/api/v1/register", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client, session):
    """Test successful login."""
    email = "test@example.com"
    password = "testpassword123"

    # Create user with properly hashed password
    user = User(
        email=email, hashed_password=get_password_hash(password), is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Use OAuth2 password flow format
    form_data = {
        "username": email,
        "password": password,
        "grant_type": "password",
    }

    response = client.post(
        "/api/v1/login/access-token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

    # Test the token works
    token = tokens["access_token"]
    response = client.post(
        "/api/v1/login/test-token", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == email


def test_login_incorrect_password(client, normal_user):
    login_data = {
        "username": normal_user.email,
        "password": "wrongpassword",
        "grant_type": "password",  # Required for OAuth2 password flow
    }
    response = client.post(
        "/api/v1/login/access-token",
        data=login_data,  # Use data instead of json for form submission
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_password_recovery(client, normal_user):
    """Test password recovery endpoint with mocked email sending"""
    with patch(
        "app.api.routes.auth.send_email", new_callable=AsyncMock
    ) as mock_send_email:
        response = client.post(f"/api/v1/password-recovery/{normal_user.email}")

        # Assert the response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Password recovery email sent"

        # Verify that send_email was called
        mock_send_email.assert_called_once()

        # Verify the call arguments using kwargs instead of args
        call_kwargs = mock_send_email.call_args.kwargs
        assert call_kwargs["email_to"] == normal_user.email
        assert "email_data" in call_kwargs
        assert "background_tasks" in call_kwargs


def test_reset_password(client, normal_user):
    # Generate a valid token
    token = create_access_token(
        subject=normal_user.email,
        expires_delta=timedelta(hours=email_reset_token_expire_hours()),
    )

    new_password = "newpassword123"
    response = client.post(
        "/api/v1/reset-password",
        json={"token": token, "new_password": new_password},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

    # Verify we can login with new password
    login_data = {
        "username": normal_user.email,
        "password": new_password,
        "grant_type": "password",
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 200
