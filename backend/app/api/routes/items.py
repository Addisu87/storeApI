# Routes for item operations
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.core.deps import CurrentUser, SessionDep
from app.models.item_models import Item, ItemCreate, ItemPublic, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


# Create an item - requires authenticated user
@router.post("/", response_model=ItemPublic, status_code=status.HTTP_201_CREATED)
def create_item(
    item: ItemCreate,
    session: SessionDep,
    current_user: CurrentUser,
):
    db_item = Item.model_validate(item, update={"owner_id": current_user.id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# Read items - returns all items (could be restricted to user's items)
@router.get("/", response_model=list[ItemPublic])
def read_items(
    session: SessionDep,
    current_user: CurrentUser,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    # Optionally filter by current_user.id if you want user-specific items
    items = session.exec(
        select(Item).where(Item.owner_id == current_user.id).offset(offset).limit(limit)
    ).all()
    return items


# Read item by ID
@router.get("/{item_id}", response_model=ItemPublic)
def read_item(item_id: UUID, session: SessionDep, current_user: CurrentUser):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    # Optional: Restrict to owner's item
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this item",
        )
    return item


# Update item by ID
@router.patch("/{item_id}", response_model=ItemPublic)
def update_item(
    item_id: UUID,
    item: ItemUpdate,
    session: SessionDep,
    current_user: CurrentUser,
):
    item_db = session.get(Item, item_id)
    if not item_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    if item_db.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item",
        )
    item_data = item.model_dump(exclude_unset=True)
    item_db.sqlmodel_update(item_data)
    session.add(item_db)
    session.commit()
    session.refresh(item_db)
    return item_db


# Delete item by ID
@router.delete("/{item_id}", response_model=dict)
def delete_item(item_id: UUID, session: SessionDep, current_user: CurrentUser):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item",
        )
    session.delete(item)
    session.commit()
    return {"message": "Item deleted"}
