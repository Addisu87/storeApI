# tests/test_email_endpoint.py
from unittest.mock import patch

import pytest
from app.core.config import settings
from app.core.deps import get_current_active_superuser
from app.main import app  # Import your FastAPI app
from app.models.schemas import EmailData
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient


# Override the dependency for testing
def override_get_current_active_superuser():
    return {"is_superuser": True}  # Mock a superuser


@pytest.fixture
def client():
    app.dependency_overrides[get_current_active_superuser] = (
        override_get_current_active_superuser
    )
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_send_test_email_endpoint(client):
    email_to = "user@example.com"

    with patch("app.services.email_services.send_email") as mock_send_email:
        response = client.post("/send-test-email/", json={"email_to": email_to})

        assert response.status_code == 201
        assert response.json() == {"message": "Email has been scheduled to be sent"}

        # Verify send_email was called with correct parameters
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]
        assert call_args[0] == email_to  # email_to
        assert isinstance(call_args[1], EmailData)  # email_data
        assert call_args[1].subject == f"{settings.PROJECT_NAME} - Test email"
        assert email_to in call_args[1].html_content
        assert isinstance(call_args[2], BackgroundTasks)  # background_tasks
