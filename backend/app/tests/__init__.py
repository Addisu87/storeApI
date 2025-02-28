"""Tests."""

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings  # type: ignore
from app.main import app

client = TestClient(app)


@pytest.mark.anyio
async def test_main():  # noqa: D103
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        assert response.json() == {"msg": "Hello Bigger Applications!"}


def test_websocket():  # noqa: D103
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data == {"msg": "Hello WebSocket"}


def get_settings_override():  # noqa: D103
    return Settings(admin_email="testing_admin@example.com")


def test_app():  # noqa: D103
    response = client.get("/info")
    data = response.json()
    assert data == {
        "project_name": "Awesome API",
        "admin_email": "testing_admin@example.com",
        "items_per_user": 50,
    }
