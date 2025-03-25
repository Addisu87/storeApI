import uuid

from sqlmodel import Session

from app.models.item_models import ItemCreate, ItemUpdate
from app.services.item_services import (
    create_item,
    delete_item,
    get_item_by_id,
    update_item,
)
from app.tests.helpers import (
    create_random_item,
    create_random_user,
    random_lower_string,
)


def test_create_item_with_owner(db: Session) -> None:
    owner = create_random_user(db)
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    item = create_item(session=db, item_in=item_in, owner_id=owner.id)
    assert item.title == title
    assert item.description == description
    assert item.owner_id == owner.id


def test_get_item(db: Session) -> None:
    owner = create_random_user(db)
    item = create_random_item(db, owner_id=owner.id)
    stored_item = get_item_by_id(session=db, item_id=item.id)
    assert stored_item
    assert item.id == stored_item.id
    assert item.title == stored_item.title
    assert item.description == stored_item.description
    assert item.owner_id == stored_item.owner_id


def test_get_item_not_found(db: Session) -> None:
    non_existent_id = uuid.uuid4()
    stored_item = get_item_by_id(session=db, item_id=non_existent_id)
    assert stored_item is None


def test_update_item(db: Session) -> None:
    owner = create_random_user(db)
    item = create_random_item(db, owner_id=owner.id)
    new_title = random_lower_string()
    updated_item = update_item(
        session=db,
        item=item,
        item_in=ItemUpdate(title=new_title, description=item.description),
    )
    assert updated_item.id == item.id
    assert updated_item.title == new_title
    assert updated_item.description == item.description
    assert updated_item.owner_id == item.owner_id


def test_delete_item(db: Session) -> None:
    owner = create_random_user(db)
    item = create_random_item(db, owner_id=owner.id)
    delete_item(session=db, item=item)
    stored_item = get_item_by_id(session=db, item_id=item.id)
    assert stored_item is None
