from fastapi import APIRouter, Query, Body, Cookie, Header, status
from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Any, Literal, Union

from datetime import datetime, time, timedelta
from uuid import UUID

# from app.routers.users import User

router = APIRouter(prefix="", tags=["items"])


class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type: str = "car"


class PlaneItem(BaseItem):
    type: str = "plane"
    size: int


# define a sub-model
class Image(BaseModel):
    url: HttpUrl
    name: str


# Item model
class Item(BaseModel):
    name: str = Field(examples=["Foo"])
    description: str | None = Field(
        default=None,
        title="The description of the item",
        max_length=300,
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None
    # set types - unique items
    # tags: set[str] = set()
    tags: list[str] = []

    # Nested models
    image: list[Image] | None = None


# class Cookies(BaseModel):
#     session_id: str
#     fatebook_tracker: str | None = None
#     googall_tracker: str | None = None


# class CommonHeaders(BaseModel):
#     # forbid extra headers
#     model_config = {"extra", "forbid"}

#     host: str
#     save_data: bool
#     if_modified_since: str | None = None
#     traceparent: str | None = None
#     x_tag: list[str] = []


# class FilterParams(BaseModel):
#     model_config = {"extra": "forbid"}

#     limit: int = Field(100, gt=0, le=100)
#     offset: int = Field(0, ge=0)
#     order_by: Literal["created_at", "updated_at"] = "created_at"
#     tags: list[str] = []


# @router.post("/")
# async def create_item(item: Item):
#     item_dict = item.model_dump()
#     if item.tax:
#         price_with_tax = item.price + item.tax
#         item_dict.update({"price_with_tax": price_with_tax})
#     return item_dict


items = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}


@router.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name", name}


# @router.get("/")
# async def read_items(
# ads_id: Annotated[str | None, Cookie()] = None
# x_token: Annotated[list[str] | None, Header()] = None
# cookies: Annotated[Cookies, Cookie()]
# headers: Annotated[CommonHeaders, Header()]
# ):
# return {"ads_id": ads_id}
# return {"X Tooken", x_token}
# return cookies
# return headers


@router.get("/items/", response_model=list[Item])
async def read_items() -> Any:
    return [{"name": "Portal Gun", "price": 42.0}, {"name": "Plumbus", "price": 32.0}]


@router.get("/items/{item_id}", response_model=Union[PlaneItem, CarItem])
async def read_item(item_id: str):
    return items[item_id]


@router.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_items(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }


@router.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Annotated[
        Item,
        Body(
            # embed=True,
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        ),
    ],
):
    results = {
        "item_id": item_id,
        "item": item,
    }
    return results


@router.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]


@router.get(
    "/items/{item_id}/public", response_model=Item, response_model_exclude=["tax"]
)
def read_item_public_data(item_id: str):
    return items[item_id]


@router.post("/items/images/multiple")
async def create_multiple_images(images: list[Image]):
    return images


# response with arbitrary dict
@router.get("/keyword-weights/", response_model=dict[str, float])
async def read_keyword_weights():
    return {"foo": 2.3, "bar": 3.4}
