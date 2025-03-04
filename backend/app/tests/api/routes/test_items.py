import uuid

from app.core.config import settings
from app.core.deps import get_current_active_superuser
from app.main import app
from app.models.schemas import Item, User
from app.tests.helpers import override_current_user
from fastapi.testclient import TestClient
from sqlmodel import Session


# ITEM CRUD TESTS (Assuming a typical item router)
# Create Item
def test_create_item_success(client: TestClient, normal_user: User, db: Session):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        json={"title": "New Item", "description": "Item Description"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Item"
    assert data["description"] == "Item Description"
    assert data["owner_id"] == str(normal_user.id)


# Read Item
def test_read_items_basic(client: TestClient, normal_user: User, db: Session):
    item = Item(title="Test Item", description="Test", owner_id=normal_user.id)
    db.add(item)
    db.commit()

    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.get(f"{settings.API_V1_STR}/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1
    assert data["data"][0]["title"] == "Test Item"


def test_read_item_by_id_success(client: TestClient, normal_user: User, db: Session):
    item = Item(title="Test Item", description="Test", owner_id=normal_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)

    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.get(f"{settings.API_V1_STR}/items/{item.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["owner_id"] == str(normal_user.id)


def test_read_item_by_id_not_found(client: TestClient, normal_user: User):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    nonexistent_id = uuid.uuid4()
    response = client.get(f"{settings.API_V1_STR}/items/{nonexistent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


# Update Item
def test_update_item_success(client: TestClient, normal_user: User, db: Session):
    item = Item(title="Test Item", description="Test", owner_id=normal_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)

    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.patch(
        f"{settings.API_V1_STR}/items/{item.id}",
        json={"title": "Updated Item", "description": "Updated Description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Item"
    assert data["description"] == "Updated Description"


def test_update_item_not_found(client: TestClient, normal_user: User):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    nonexistent_id = uuid.uuid4()
    response = client.patch(
        f"{settings.API_V1_STR}/items/{nonexistent_id}",
        json={"title": "Updated Item"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


# Delete Item
def test_delete_item_success(client: TestClient, normal_user: User, db: Session):
    item = Item(title="Test Item", description="Test", owner_id=normal_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)

    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    response = client.delete(f"{settings.API_V1_STR}/items/{item.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Item deleted successfully"
    assert db.get(Item, item.id) is None


def test_delete_item_not_found(client: TestClient, normal_user: User):
    app.dependency_overrides[get_current_active_superuser] = override_current_user(
        normal_user
    )
    nonexistent_id = uuid.uuid4()
    response = client.delete(f"{settings.API_V1_STR}/items/{nonexistent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
