# Item-related business logic

import uuid

from sqlmodel import Session

from app.schemas.items import Item, ItemCreate


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """Create a new item.

    Args:
        session (Session): The database session.
        item_in (ItemCreate): The item input data.
        owner_id (uuid.UUID): The owner id.

    Returns:
        Item: The created item.

    """
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
