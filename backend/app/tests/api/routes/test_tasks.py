from unittest.mock import patch

from app.core.config import settings
from app.models.email_models import EmailData
from fastapi.testclient import TestClient


def test_send_test_email_endpoint(
    client: TestClient, superuser_token_headers: dict[str, str]
):
    """Test the send test email endpoint."""
    email_to = "user@example.com"

    # Mock the template rendering to avoid file system dependencies
    with (
        patch("app.services.email_services.render_email_template") as mock_render,
        patch("app.api.routes.tasks.send_email") as mock_send,
    ):
        # Setup mock return value for template rendering
        mock_render.return_value = f"<p>Test email content for {email_to}</p>"

        response = client.post(
            f"{settings.API_V1_STR}/send-test-email/",
            headers=superuser_token_headers,
            json={"email_to": email_to},
        )

        assert response.status_code == 201
        assert response.json() == {"message": "Email has been scheduled to be sent"}

        # Verify template rendering was called correctly
        mock_render.assert_called_once_with(
            template_name="test_email.mjml",
            context={"project_name": settings.PROJECT_NAME, "email": email_to},
        )

        # Verify send_email was called with correct arguments
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        assert args[0] == email_to  # First arg is email_to
        assert isinstance(args[1], EmailData)  # Second arg is EmailData
        assert args[1].subject == f"{settings.PROJECT_NAME} - Test email"
        assert "Test email content" in args[1].html_content


def test_health_check_endpoint(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/health-check/")
    assert response.status_code == 200
    assert response.json() is True
