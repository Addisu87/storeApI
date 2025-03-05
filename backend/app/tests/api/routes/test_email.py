from unittest.mock import patch

from app.core.config import settings
from app.models.schemas import EmailData
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient


def test_send_test_email_endpoint(
    client: TestClient, superuser_token_headers: dict[str, str]
):
    email_to = "user@example.com"

    with patch("app.services.email_services.send_email") as mock_send_email:
        response = client.post(
            f"{settings.API_V1_STR}/send-test-email/",
            headers=superuser_token_headers,
            json={"email_to": email_to},
        )

        assert response.status_code == 201
        assert response.json() == {"message": "Email has been scheduled to be sent"}

        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]
        assert call_args[0] == email_to
        assert isinstance(call_args[1], EmailData)
        assert call_args[1].subject == f"{settings.PROJECT_NAME} - Test email"
        assert email_to in call_args[1].html_content
        assert isinstance(call_args[2], BackgroundTasks)
