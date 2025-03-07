from unittest.mock import patch

from app.core.config import settings
from app.models.email_models import EmailData
from fastapi.testclient import TestClient


def test_send_test_email_endpoint(
    client: TestClient, superuser_token_headers: dict[str, str]
):
    email_to = "user@example.com"

    with patch("app.services.email_services.send_email_background") as mock_send_email:
        response = client.post(
            f"{settings.API_V1_STR}/send-test-email/",
            headers=superuser_token_headers,
            json={"email_to": email_to},
        )

        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.text}"
        )
        assert response.json() == {"message": "Email has been scheduled to be sent"}

        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]
        assert call_args[0] == email_to
        assert isinstance(call_args[1], EmailData)
        assert call_args[1].subject == f"{settings.PROJECT_NAME} - Test email"
        assert email_to in call_args[1].html_content


def test_health_check_endpoint(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/health-check/")
    assert response.status_code == 200
    assert response.json() is True
