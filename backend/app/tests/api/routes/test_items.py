# app/tests/api/routes/test_items.py
import pytest
import uuid
from typing import Dict

from fastapi import status
from app.core.config import settings
from app.models.item_models import Item
from app.models.user_models import User
from app.tests.helpers import create_random_item, random_lower_string
from fastapi.testclient import TestClient
from sqlmodel import Session


# ITEM CRUD TESTS
def test_create_item(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
    db: Session,
) -> None:
    data = {"title": "Test Item", "description": "Test Description"}
    response = client.post(
        "/api/v1/items/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_create_item_for_user(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    title = random_lower_string()
    description = random_lower_string()
    data = {"title": title, "description": description}
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    assert content["title"] == title
    assert content["description"] == description
    assert "id" in content
    assert "owner_id" in content


def test_read_item(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
    db: Session,
) -> None:
    item = create_random_item(db)
    response = client.get(
        f"/api/v1/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == item.title
    assert content["description"] == item.description
    assert content["id"] == str(item.id)
    assert "owner_id" in content


def test_update_item(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
    db: Session,
) -> None:
    item = create_random_item(db)
    data = {"title": "Updated Title"}
    response = client.patch(
        f"/api/v1/items/{item.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == item.description
    assert content["id"] == str(item.id)


def test_delete_item(
    client: TestClient,
    normal_user_token_headers: Dict[str, str],
    db: Session,
) -> None:
    item = create_random_item(db)
    response = client.delete(
        f"/api/v1/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify item is deleted
    response = client.get(
        f"/api/v1/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404


def test_read_item_by_id_success(
    client: TestClient,
    normal_user: User,
    db: Session,
    normal_user_token_headers: dict[str, str],
):
    item = Item(title="Test Item", description="Test", owner_id=normal_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)

    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}", headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["description"] == "Test"
    assert data["owner_id"] == str(normal_user.id)
    assert data["id"] == str(item.id)


def test_read_item_by_id_not_found(
    client: TestClient, normal_user_token_headers: dict[str, str]
):
    nonexistent_id = uuid.uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/items/{nonexistent_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_read_item_by_id_forbidden(
    client: TestClient,
    normal_user: User,
    db: Session,
    normal_user_token_headers: dict[str, str],
):
    # Create an item owned by a different user
    other_user = User(
        email="other@example.com",
        hashed_password="hashedpassword",
        is_active=True,
        is_superuser=False,
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    item = Item(title="Other Item", description="Other", owner_id=other_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)

    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}", headers=normal_user_token_headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to access this item"


def test_update_item_success(
    client: TestClient,
    normal_user: User,
    db: Session,
    normal_user_token_headers: dict[str, str],
):
    item = Item(title="Test Item", description="Test", owner_id=normal_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)

    response = client.patch(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
        json={"title": "Updated Item", "description": "Updated Description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Item"
    assert data["description"] == "Updated Description"
    assert data["owner_id"] == str(normal_user.id)


def test_update_item_not_found(
    client: TestClient, normal_user_token_headers: dict[str, str]
):
    nonexistent_id = uuid.uuid4()
    response = client.patch(
        f"{settings.API_V1_STR}/items/{nonexistent_id}",
        headers=normal_user_token_headers,
        json={"title": "Updated Item"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_update_item_forbidden(
    client: TestClient,
    normal_user: User,
    db: Session,
    normal_user_token_headers: dict[str, str],
):
    other_user = User(
        email="other@example.com",
        hashed_password="hashedpassword",
        is_active=True,
        is_superuser=False,
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    item = Item(title="Other Item", description="Other", owner_id=other_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)

    response = client.patch(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
        json={"title": "Updated Item"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this item"


def test_delete_item_success(
    client: TestClient,
    normal_user: User,
    db: Session,
    normal_user_token_headers: dict[str, str],
):
    item = Item(title="Test Item", description="Test", owner_id=normal_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)

    response = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}", headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Item deleted"}
    assert db.get(Item, item.id) is None


def test_delete_item_not_found(
    client: TestClient, normal_user_token_headers: dict[str, str]
):
    nonexistent_id = uuid.uuid4()
    response = client.delete(
        f"{settings.API_V1_STR}/items/{nonexistent_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_delete_item_forbidden(
    client: TestClient,
    normal_user: User,
    db: Session,
    normal_user_token_headers: dict[str, str],
):
    other_user = User(
        email="other@example.com",
        hashed_password="hashedpassword",
        is_active=True,
        is_superuser=False,
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    item = Item(title="Other Item", description="Other", owner_id=other_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)

    response = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}", headers=normal_user_token_headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this item"


def test_unauthorized_operations(client, test_item):
    # Try operations without authentication
    endpoints = [
        ("GET", f"/api/v1/items/{test_item.id}"),
        ("GET", "/api/v1/items/"),
        ("POST", "/api/v1/items/"),
        ("PATCH", f"/api/v1/items/{test_item.id}"),
        ("DELETE", f"/api/v1/items/{test_item.id}"),
    ]
    
    for method, endpoint in endpoints:
        response = client.request(method, endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "item_data,expected_status",
    [
        ({"title": ""}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"title": "a" * 256}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
def test_create_item_validation(
    client, 
    normal_user_token_headers, 
    item_data, 
    expected_status
):
    response = client.post(
        "/api/v1/items/",
        headers=normal_user_token_headers,
        json=item_data,
    )
    assert response.status_code == expected_status


def test_read_items(client, normal_user, normal_user_token_headers, session):
    # Create multiple items
    items_count = 3
    for _ in range(items_count):
        create_random_item(session, owner_id=normal_user.id)
    
    response = client.get(
        "/api/v1/items/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert content["count"] >= items_count
    assert len(content["data"]) >= items_count
