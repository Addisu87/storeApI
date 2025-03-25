# Routes for item operations
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import func, select

from app.core.deps import CurrentUser, SessionDep
from app.models.item_models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.services.item_services import create_item, get_item_by_id

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemPublic, status_code=status.HTTP_201_CREATED)
def create_item_route(
    item: ItemCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Item:
    """Create a new item."""
    return create_item(session=session, item_in=item, owner_id=current_user.id)


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep,
    current_user: CurrentUser,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> ItemsPublic:
    """Get all items for the current user with pagination."""
    items = session.exec(
        select(Item).where(Item.owner_id == current_user.id).offset(offset).limit(limit)
    ).all()
    total = session.exec(
        select(func.count()).select_from(Item).where(Item.owner_id == current_user.id)
    ).first()
    return ItemsPublic(
        data=[ItemPublic.model_validate(item) for item in items], count=total or 0
    )


@router.get("/{item_id}", response_model=ItemPublic)
def read_item(
    item_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Item:
    """Get a specific item by ID."""
    item = get_item_by_id(session=session, item_id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this item",
        )
    return item


@router.patch("/{item_id}", response_model=ItemPublic)
def update_item(
    item_id: UUID,
    item: ItemUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Item:
    """Update an item."""
    db_item = get_item_by_id(session=session, item_id=item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    if db_item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item",
        )
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete("/{item_id}", response_model=dict)
def delete_item(
    item_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """Delete an item."""
    item = get_item_by_id(session=session, item_id=item_id)
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
