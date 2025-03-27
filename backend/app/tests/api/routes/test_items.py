# app/tests/api/routes/test_items.py
from typing import Dict
from uuid import uuid4

from app.core.config import settings
from app.models.user_models import User
from app.tests.helpers import create_random_item
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session


# ITEM CRUD TESTS
def test_create_item(
    client: TestClient,
    normal_user: User,
    normal_user_token_headers: Dict[str, str],
    session: Session,
) -> None:
    data = {"title": "Test Item", "description": "Test Description"}
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content
    assert content["owner_id"] == str(normal_user.id)


def test_read_item(
    client: TestClient,
    normal_user: User,
    normal_user_token_headers: Dict[str, str],
    session: Session,
) -> None:
    item = create_random_item(session, owner_id=normal_user.id)
    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == item.title
    assert content["description"] == item.description
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(normal_user.id)


def test_read_items(
    client: TestClient,
    normal_user: User,
    normal_user_token_headers: Dict[str, str],
    session: Session,
) -> None:
    # Create multiple items
    items_count = 3
    for _ in range(items_count):
        create_random_item(session, owner_id=normal_user.id)

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert content["count"] >= items_count
    assert len(content["data"]) >= items_count


def test_update_item(
    client: TestClient,
    normal_user: User,
    normal_user_token_headers: Dict[str, str],
    session: Session,
) -> None:
    item = create_random_item(session, owner_id=normal_user.id)
    data = {"title": "Updated Title"}
    response = client.patch(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == item.description
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(normal_user.id)


def test_delete_item(
    client: TestClient,
    normal_user: User,
    normal_user_token_headers: Dict[str, str],
    session: Session,
) -> None:
    item = create_random_item(session, owner_id=normal_user.id)
    response = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Item deleted"

    # Verify item is deleted
    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_item_not_found(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
) -> None:
    nonexistent_id = uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/items/{nonexistent_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item not found"


def test_read_item_forbidden(
    client: TestClient,
    normal_user: User,
    other_user: User,
    normal_user_token_headers: Dict[str, str],
    session: Session,
) -> None:
    item = create_random_item(session, owner_id=other_user.id)
    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized to access this item"


def test_update_item_not_found(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
) -> None:
    nonexistent_id = uuid4()
    response = client.patch(
        f"{settings.API_V1_STR}/items/{nonexistent_id}",
        headers=normal_user_token_headers,
        json={"title": "Updated Item"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item not found"


def test_update_item_forbidden(
    client: TestClient,
    normal_user: User,
    other_user: User,
    normal_user_token_headers: Dict[str, str],
    session: Session,
) -> None:
    item = create_random_item(session, owner_id=other_user.id)
    response = client.patch(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
        json={"title": "Updated Item"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized to update this item"


def test_delete_item_not_found(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
) -> None:
    nonexistent_id = uuid4()
    response = client.delete(
        f"{settings.API_V1_STR}/items/{nonexistent_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item not found"


def test_delete_item_forbidden(
    client: TestClient,
    normal_user: User,
    other_user: User,
    normal_user_token_headers: Dict[str, str],
    session: Session,
) -> None:
    item = create_random_item(session, owner_id=other_user.id)
    response = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized to delete this item"
