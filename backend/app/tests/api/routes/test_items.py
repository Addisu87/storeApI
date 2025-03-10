# app/tests/api/routes/test_items.py
import uuid

from app.core.config import settings
from app.models.item_models import Item
from app.models.user_models import User
from fastapi.testclient import TestClient
from sqlmodel import Session


# ITEM CRUD TESTS
def test_create_item_success(
    client: TestClient,
    normal_user: User,
    normal_user_token_headers: dict[str, str],
    db: Session,
):
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=normal_user_token_headers,
        json={"title": "New Item", "description": "Item Description"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Item"
    assert data["description"] == "Item Description"
    assert data["owner_id"] == str(normal_user.id)
    assert uuid.UUID(data["id"])  # Ensure ID is a valid UUID


def test_read_items_basic(
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
        f"{settings.API_V1_STR}/items/", headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Expect a list of items
    assert len(data) >= 1
    assert data[0]["title"] == "Test Item"
    assert data[0]["owner_id"] == str(normal_user.id)


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
