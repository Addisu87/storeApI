# app/tests/api/routes/test_tasks.py
from unittest.mock import patch

import pytest
from app.core.config import settings
from app.core.deps import get_current_active_superuser
from app.main import app
from app.models.schemas import EmailData
from app.services.email_services import send_email_background
from fastapi.testclient import TestClient


def override_get_current_active_superuser():
    return {"is_superuser": True}


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
    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        response = client.post("/api/v1/send-test-email/", json={"email_to": email_to})
        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.text}"
        )
        assert response.json() == {"message": "Email has been scheduled to be sent"}

        # Verify the task was scheduled
        mock_add_task.assert_called_once()
        call_args = mock_add_task.call_args[0]
        assert (
            call_args[0] == send_email_background
        )  # Compare with the imported function
        assert call_args[1] == email_to
        assert isinstance(call_args[2], EmailData)
        assert call_args[2].subject == f"{settings.PROJECT_NAME} - Test email"
        assert email_to in call_args[2].html_content


def test_health_check_endpoint(client):
    response = client.get("/api/v1/health-check/")
    assert response.status_code == 200
    assert response.json() is True
