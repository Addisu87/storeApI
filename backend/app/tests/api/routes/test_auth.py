from unittest.mock import patch

from app.core.config import get_settings
from app.core.security import verify_password
from app.models.schemas import User
from app.services.user_services import get_user_by_email
from app.tests.conftest import create_random_user_fixture
from fastapi.testclient import TestClient
from sqlmodel import Session


# REGISTER TESTS
def test_register_user_success(client: TestClient, db: Session):
    """Test registering a new user successfully."""
    email = "newuser@example.com"
    response = client.post(
        f"{get_settings('test').API_V1_STR}/register",
        json={"email": email, "password": "TestPass123!", "full_name": "New User"},
    )
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    data = response.json()
    assert data["email"] == email
    assert data["full_name"] == "New User"
    assert "id" in data
    assert data["is_active"] is True
    assert data["is_superuser"] is False
    # Verify user in DB
    user = get_user_by_email(db, email)
    assert user is not None
    assert verify_password("TestPass123!", user.hashed_password)


def test_register_user_duplicate_email(client: TestClient, normal_user: User):
    """Test registering a user with an existing email."""
    response = client.post(
        f"{get_settings('test').API_V1_STR}/register",
        json={
            "email": normal_user.email,
            "password": "TestPass123!",
            "full_name": "Duplicate User",
        },
    )
    assert response.status_code == 400, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "A user with that email already exists!"


def test_register_user_invalid_password(client: TestClient):
    """Test registering with a password that's too short."""
    response = client.post(
        f"{get_settings('test').API_V1_STR}/register",
        json={
            "email": "shortpass@example.com",
            "password": "short",
            "full_name": "Short Pass",
        },
    )
    assert response.status_code == 422, f"Got {response.status_code}: {response.text}"
    assert "ensure this value has at least 8 characters" in response.text


def test_register_user_missing_fields(client: TestClient):
    """Test registering with missing required fields."""
    response = client.post(
        f"{get_settings('test').API_V1_STR}/register",
        json={
            "email": "missing@example.com"
            # No password
        },
    )
    assert response.status_code == 422, f"Got {response.status_code}: {response.text}"
    assert "field required" in response.text


# LOGIN TESTS
def test_login_success(client: TestClient, normal_user: User):
    """Test logging in with valid credentials."""
    response = client.post(
        f"{get_settings('test').API_V1_STR}/login/access-token",
        json={"email": normal_user.email, "password": "usersecret"},
    )
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, normal_user: User):
    """Test logging in with an incorrect password."""
    response = client.post(
        f"{get_settings('test').API_V1_STR}/login/access-token",
        json={"email": normal_user.email, "password": "wrongsecret"},
    )
    assert response.status_code == 401, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_nonexistent_user(client: TestClient):
    """Test logging in with a non-existent user."""
    response = client.post(
        f"{get_settings('test').API_V1_STR}/login/access-token",
        json={"email": "nonexistent@example.com", "password": "TestPass123!"},
    )
    assert response.status_code == 401, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_inactive_user(client: TestClient, db: Session):
    """Test logging in with an inactive user."""
    user = create_random_user_fixture(db)()
    user.is_active = False
    db.add(user)
    db.commit()
    response = client.post(
        f"{get_settings('test').API_V1_STR}/login/access-token",
        json={
            "email": user.email,
            "password": user.email.split("@")[
                0
            ],  # Assuming password is email prefix from random creation
        },
    )
    assert response.status_code == 401, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "Inactive user"


# TEST TOKEN TESTS
def test_test_token_success(
    client: TestClient, normal_user_token_headers: dict[str, str]
):
    """Test validating a token successfully."""
    response = client.post(
        f"{get_settings('test').API_V1_STR}/login/test-token",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    data = response.json()
    assert data["email"] == "user@example.com"


def test_test_token_no_auth(client: TestClient):
    """Test accessing test-token without authentication."""
    response = client.post(f"{get_settings('test').API_V1_STR}/login/test-token")
    assert response.status_code == 401, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "Not authenticated"


def test_test_token_invalid_token(client: TestClient):
    """Test accessing test-token with an invalid token."""
    response = client.post(
        f"{get_settings('test').API_V1_STR}/login/test-token",
        headers={"Authorization": "Bearer invalid_token_here"},
    )
    assert response.status_code == 401, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "Could not validate credentials"


# RESET PASSWORD TESTS (Mocked since logic is incomplete)
def test_reset_password_success(client: TestClient, db: Session, normal_user: User):
    """Test resetting password with a valid token (mocked)."""
    with patch(
        "app.services.password_services.verify_password_reset_token",
        return_value=normal_user.email,
    ):
        response = client.post(
            f"{get_settings('test').API_V1_STR}/reset-password",
            json={"token": "valid_reset_token", "new_password": "NewPass123!"},
        )
        assert response.status_code == 200, (
            f"Got {response.status_code}: {response.text}"
        )
        assert response.json()["message"] == "Password updated successfully"
        db.refresh(normal_user)
        assert verify_password("NewPass123!", normal_user.hashed_password)


def test_reset_password_invalid_token(client: TestClient):
    """Test resetting password with an invalid token."""
    with patch(
        "app.services.password_services.verify_password_reset_token", return_value=None
    ):
        response = client.post(
            f"{get_settings('test').API_V1_STR}/reset-password",
            json={"token": "invalid_token", "new_password": "NewPass123!"},
        )
        assert response.status_code == 400, (
            f"Got {response.status_code}: {response.text}"
        )
        assert response.json()["detail"] == "Invalid token"


def test_reset_password_nonexistent_user(client: TestClient):
    """Test resetting password for a non-existent user."""
    with patch(
        "app.services.password_services.verify_password_reset_token",
        return_value="nonexistent@example.com",
    ):
        response = client.post(
            f"{get_settings('test').API_V1_STR}/reset-password",
            json={"token": "some_token", "new_password": "NewPass123!"},
        )
        assert response.status_code == 404, (
            f"Got {response.status_code}: {response.text}"
        )
        assert (
            response.json()["detail"]
            == "A user with this email does not exist in the system!"
        )


def test_reset_password_inactive_user(client: TestClient, db: Session):
    """Test resetting password for an inactive user."""
    user = create_random_user_fixture(db)()
    user.is_active = False
    db.add(user)
    db.commit()
    with patch(
        "app.services.password_services.verify_password_reset_token",
        return_value=user.email,
    ):
        response = client.post(
            f"{get_settings('test').API_V1_STR}/reset-password",
            json={"token": "some_token", "new_password": "NewPass123!"},
        )
        assert response.status_code == 400, (
            f"Got {response.status_code}: {response.text}"
        )
        assert response.json()["detail"] == "Inactive user"
