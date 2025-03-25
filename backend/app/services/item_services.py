# Item-related business logic
import uuid
from typing import Optional

from sqlmodel import Session, func, select

from app.models.item_models import Item, ItemCreate, ItemUpdate


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """Create a new item."""
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_item_by_id(*, session: Session, item_id: uuid.UUID) -> Optional[Item]:
    """Get an item by ID."""
    return session.get(Item, item_id)


def get_items_by_owner(
    *, session: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> tuple[list[Item], int]:
    """Get all items for a specific owner with pagination."""
    items = session.exec(
        select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
    ).all()
    total = session.exec(
        select(func.count()).select_from(Item).where(Item.owner_id == owner_id)
    ).first()
    return list(items), total or 0


def update_item(*, session: Session, item: Item, item_in: ItemUpdate) -> Item:
    """Update an item."""
    item_data = item_in.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_item(*, session: Session, item: Item) -> None:
    """Delete an item."""
    session.delete(item)
    session.commit()


def get_items(
    *, session: Session, skip: int = 0, limit: int = 100
) -> tuple[list[Item], int]:
    """Get all items with pagination."""
    items = session.exec(select(Item).offset(skip).limit(limit)).all()
    total = session.exec(select(func.count()).select_from(Item)).first()
    return list(items), total or 0


def get_items_count(*, session: Session) -> int:
    """Get total count of items."""
    return session.exec(select(func.count()).select_from(Item)).first() or 0


def get_items_by_title(
    *, session: Session, title: str, skip: int = 0, limit: int = 100
) -> tuple[list[Item], int]:
    """Get items by title (case-insensitive) with pagination."""
    items = session.exec(
        select(Item)
        .where(func.lower(Item.title).contains(title.lower()))
        .offset(skip)
        .limit(limit)
    ).all()
    total = session.exec(
        select(func.count())
        .select_from(Item)
        .where(func.lower(Item.title).contains(title.lower()))
    ).first()
    return list(items), total or 0


def get_items_by_owner_and_title(
    *,
    session: Session,
    owner_id: uuid.UUID,
    title: str,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Item], int]:
    """Get items by owner and title (case-insensitive) with pagination."""
    items = session.exec(
        select(Item)
        .where(Item.owner_id == owner_id)
        .where(func.lower(Item.title).contains(title.lower()))
        .offset(skip)
        .limit(limit)
    ).all()
    total = session.exec(
        select(func.count())
        .select_from(Item)
        .where(Item.owner_id == owner_id)
        .where(func.lower(Item.title).contains(title.lower()))
    ).first()
    return list(items), total or 0
