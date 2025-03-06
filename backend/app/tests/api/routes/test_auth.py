import uuid
from unittest.mock import patch

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models.schemas import User
from app.services.user_services import get_user_by_email
from fastapi.testclient import TestClient
from sqlmodel import Session


# REGISTER TESTS
def test_register_user_success(client: TestClient, db: Session):
    email = f"newuser-{uuid.uuid4()}@example.com"  # Unique email per test
    response = client.post(
        f"{settings.API_V1_STR}/register",
        json={"email": email, "password": "TestPass123!"},
    )
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    data = response.json()
    assert data["email"] == email
    assert data["full_name"] is None
    assert "id" in data
    assert data["is_active"] is True
    assert data["is_superuser"] is False
    user = get_user_by_email(db, email)
    assert user is not None
    assert verify_password("TestPass123!", user.hashed_password)


def test_register_user_duplicate_email(client: TestClient, normal_user: User):
    response = client.post(
        f"{settings.API_V1_STR}/register",
        json={"email": normal_user.email, "password": "TestPass123!"},
    )
    assert response.status_code == 400, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "A user with that email already exists!"


def test_register_user_invalid_password(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/register",
        json={"email": "shortpass@example.com", "password": "short"},
    )
    assert response.status_code == 422, f"Got {response.status_code}: {response.text}"
    assert "string_too_short" in response.text


def test_register_user_missing_fields(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/register",
        json={"email": "missing@example.com"},
    )
    assert response.status_code == 422, f"Got {response.status_code}: {response.text}"
    assert "missing" in response.text


# LOGIN TESTS
def test_login_success(client: TestClient, normal_user: User):
    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        json={"email": normal_user.email, "password": "usersecret"},
    )
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, normal_user: User):
    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        json={"email": normal_user.email, "password": "wrongsecret"},
    )
    assert response.status_code == 401, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_nonexistent_user(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        json={"email": "nonexistent@example.com", "password": "TestPass123!"},
    )
    assert response.status_code == 401, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_inactive_user(
    client: TestClient, db: Session, create_random_user_fixture
):
    user = create_random_user_fixture()
    user.hashed_password = get_password_hash("testpass")  # Set a known password
    user.is_active = False
    db.add(user)
    db.commit()
    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        json={"email": user.email, "password": "testpass"},
    )
    assert response.status_code == 401, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "Inactive user"


# TEST TOKEN TESTS
def test_test_token_success(
    client: TestClient, normal_user_token_headers: dict[str, str]
):
    response = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    data = response.json()
    assert data["email"] == "user@example.com"


def test_test_token_no_auth(client: TestClient):
    response = client.post(f"{settings.API_V1_STR}/login/test-token")
    assert response.status_code == 401, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "Not authenticated"


def test_test_token_invalid_token(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers={"Authorization": "Bearer invalid_token_here"},
    )
    assert response.status_code == 401, f"Got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "Could not validate credentials"


# RESET PASSWORD TESTS
def test_reset_password_success(client: TestClient, db: Session, normal_user: User):
    with patch(
        "app.api.routes.auth.verify_password_reset_token"
    ) as mock_verify:  # Patch at endpoint level
        mock_verify.return_value = normal_user.email
        response = client.post(
            f"{settings.API_V1_STR}/reset-password",
            json={"token": "valid_reset_token", "new_password": "NewPass123!"},
        )
        assert response.status_code == 200, (
            f"Got {response.status_code}: {response.text}"
        )
        assert response.json()["message"] == "Password updated successfully"
        db.refresh(normal_user)
        assert verify_password("NewPass123!", normal_user.hashed_password)


def test_reset_password_invalid_token(client: TestClient):
    with patch("app.api.routes.auth.verify_password_reset_token") as mock_verify:
        mock_verify.return_value = None
        response = client.post(
            f"{settings.API_V1_STR}/reset-password",
            json={"token": "invalid_token", "new_password": "NewPass123!"},
        )
        assert response.status_code == 400, (
            f"Got {response.status_code}: {response.text}"
        )
        assert response.json()["detail"] == "Invalid token"


def test_reset_password_nonexistent_user(client: TestClient):
    with patch("app.api.routes.auth.verify_password_reset_token") as mock_verify:
        mock_verify.return_value = "nonexistent@example.com"
        response = client.post(
            f"{settings.API_V1_STR}/reset-password",
            json={"token": "some_token", "new_password": "NewPass123!"},
        )
        assert response.status_code == 404, (
            f"Got {response.status_code}: {response.text}"
        )
        assert (
            response.json()["detail"]
            == "A user with this email does not exist in the system!"
        )


def test_reset_password_inactive_user(
    client: TestClient, db: Session, create_random_user_fixture
):
    user = create_random_user_fixture()
    user.hashed_password = get_password_hash("testpass")  # Set a known password
    user.is_active = False
    db.add(user)
    db.commit()
    with patch("app.api.routes.auth.verify_password_reset_token") as mock_verify:
        mock_verify.return_value = user.email
        response = client.post(
            f"{settings.API_V1_STR}/reset-password",
            json={"token": "some_token", "new_password": "NewPass123!"},
        )
        assert response.status_code == 400, (
            f"Got {response.status_code}: {response.text}"
        )
        assert response.json()["detail"] == "Inactive user"
