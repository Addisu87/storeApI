# Routes for item operations
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.core.deps import SessionDep
from app.schemas.items import Item, ItemCreate, ItemPublic, ItemUpdate

router = APIRouter(prefix="", tags=["items"])


# Create a item -
# ensure data is validated and serialized correctly(response_model)
@router.post("/items/", response_model=ItemPublic)
def create_item(item: ItemCreate, session: SessionDep):
    db_item = item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# Read items - ensure data is validated and serialized correctly
@router.get("/items/", response_model=list[ItemPublic])
def read_items(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    items = session.exec(select(Item).offset(offset).limit(limit)).all()
    return items


# Read item by Id
@router.get("/items/{item_id}", response_model=ItemPublic)
def read_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="item not found"
        )
    return item


# Update item by Id
@router.patch("/items/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, item: ItemUpdate, session: SessionDep):
    item_db = session.get(Item, item_id)
    if not item_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    # only the data sent by the client
    item_data = item.model_dump(exclude_unset=True)
    item_db.sqlmodel_update(item_data)
    session.add(item_db)
    session.commit()
    session.refresh(item_db)
    return item_db


# Delete item
@router.delete("/items/{item_id}")
def delete_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    session.delete(item)
    session.commit()
    return {"ok": True}
