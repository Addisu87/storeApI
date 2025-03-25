# Mock settings to use a very short expiration time
from unittest.mock import patch

from app.services.password_services import (
    generate_password_reset_token,
    verify_password_reset_token,
)


def test_password_reset_token_flow():
    email = "test@example.com"

    # Generate token
    token = generate_password_reset_token(email)
    assert token

    # Verify token
    verified_email = verify_password_reset_token(token)
    assert verified_email == email


def test_expired_token():
    with patch(
        "app.services.password_services.email_reset_token_expire_hours", return_value=0
    ):
        email = "test@example.com"
        token = generate_password_reset_token(email)

        # Wait a moment to ensure token expires
        import time

        time.sleep(1)

        result = verify_password_reset_token(token)
        assert result is None


def test_invalid_token():
    invalid_token = "invalid.token.here"
    result = verify_password_reset_token(invalid_token)
    assert result is None
