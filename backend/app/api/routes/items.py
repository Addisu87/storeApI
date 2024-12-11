# Routes for item operations
from fastapi import APIRouter, Body, status, HTTPException, Depends, Header, status
from fastapi.encoders import jsonable_encoder

from typing import Annotated

from datetime import datetime, time, timedelta
from uuid import UUID

from app.core.security import oauth2_scheme

from app.core.deps import get_token_header
from app.api.schemas.items import Item


# from app.routers.users import User

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

fake_secret_token = "coneofsilence"

fake_db = {
    "foo": {"id": "foo", "title": "Foo", "description": "There goes my hero"},
    "bar": {"id": "bar", "title": "Bar", "description": "The bartenders"},
}


fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.post(
    "/",
    response_model=Item,
    summary="Create an Item",
    status_code=status.HTTP_201_CREATED,
)
async def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    \f
    :param item: User input.
    """

    return item


# Get items
@router.get("/")
async def read_items():
    return fake_items_db


# Get individual item
@router.get("/{item_id}")
async def read_item(item_id: str):
    if item_id not in fake_items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return {"name": fake_items_db[item_id]["name"], "item_id": item_id}


# Update item
@router.put(
    "/{item_id}",
    tags=["custom"],
    responses={403: {"description": "Operation forbidden"}},
)
async def update_item(item_id: str):
    if item_id != "plumbus":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update the item: plumbus",
        )
    return {"item_id": item_id, "name": "The great Plumbus"}
