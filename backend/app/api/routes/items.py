# Routes for item operations
from fastapi import (
    APIRouter,
    Body,
    status,
    HTTPException,
    Depends,
)
from fastapi.encoders import jsonable_encoder


from typing import Annotated

from datetime import datetime, time, timedelta
from uuid import UUID

# from api.dependencies.common_query import (
#     CommonQueryParams,
#     query_or_cookie_extractor,
# )

from app.api.schemas.items import Image, Item, CarItem, PlaneItem
from app.core.security import oauth2_scheme


# from app.routers.users import User

router = APIRouter(prefix="", tags=["items"])

fake_db = {}


# @router.post("/")
# async def create_item(item: Item):
#     item_dict = item.model_dump()
#     if item.tax:
#         price_with_tax = item.price + item.tax
#         item_dict.update({"price_with_tax": price_with_tax})
#     return item_dict

items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

data = {
    "plumbs": {"description": "Freshly pickled plumbs", "owner": "Morty"},
    "portal-gun": {"description": "Gun to create portals", "owner": "Rick"},
}


# class OwnerError(Exception):
#     pass


# def get_username():
#     try:
#         yield "Rick"
#     except OwnerError as e:
#         raise HTTPException(status_code=400, detail=f"Owner error: {e}")


# Alternatively
class InternalError(Exception):
    pass


def get_username():
    try:
        yield "Rick"
    except InternalError:
        print("We don't swallow the internal error here, we raise again 😎")
        raise


@router.post(
    "/items/",
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
    """
    return item


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


# Add dependencies to the path operation decorator
# @router.get("/items/", response_model=list[Item])
# async def read_items(commons: Annotated[CommonQueryParams, Depends()]):
#     response = {}
#     if commons.q:
#         response.update({"q", commons.q})
#     items = fake_items_db[commons.skip : commons.skip + commons.limit]
#     response.update({"items": items})
#     return response


# @router.get("/items/query/")
# async def read_query(
#     query_or_default: Annotated[str | None, Depends(query_or_cookie_extractor)] = None
# ):
#     return {"q_or_cookie": query_or_default}


# @router.get(
#     "/items/{item_id}",
#     # response_model=Union[PlaneItem, CarItem],
# )
# async def read_item(item_id: str, username: Annotated[str, Depends(get_username)]):
#     if item_id not in data:
#         raise HTTPException(status_code=404, detail="Item not found")
#     item = data[item_id]
#     if item["owner"] != username:
#         raise OwnerError(username)
#     return item


# @router.get(
#     "/items/{item_id}",
# )
# async def read_item(item_id: str, username: Annotated[str, Depends(get_username)]):
#     if item_id == "portal-gun":
#         raise InternalError(
#             f"The portal gun is too dangerous to be owned by {username}"
#         )
#     if item_id != "plumbus":
#         raise HTTPException(
#             status_code=404, detail="Item not found, there's only a plumbus here"
#         )
#     return item_id


# @router.get("/items/{item_id}", response_model=Item)
# async def read_item(item_id: str):
#     # if item_id == 3:
#     #     raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
#     return items[item_id]


# Get Current User
# @router.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}


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


# @router.put("/items/{item_id}", response_model=Item)
# def update_item(item_id: str, item: Item):
#     update_item_encoded = jsonable_encoder(item)
#     # fake_db[item_id] = update_item_encoded
#     items[item_id] = update_item_encoded
#     return update_item_encoded


# @router.put("/items/{item_id}")
# async def update_item(
#     *,
#     item_id: int,
#     item: Annotated[
#         Item,
#         Body(
#             # embed=True,
#             openapi_examples={
#                 "normal": {
#                     "summary": "A normal example",
#                     "description": "A **normal** item works correctly.",
#                     "value": {
#                         "name": "Foo",
#                         "description": "A very nice Item",
#                         "price": 35.4,
#                         "tax": 3.2,
#                     },
#                 },
#                 "converted": {
#                     "summary": "An example with converted data",
#                     "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
#                     "value": {
#                         "name": "Bar",
#                         "price": "35.4",
#                     },
#                 },
#                 "invalid": {
#                     "summary": "Invalid data is rejected with an error",
#                     "value": {
#                         "name": "Baz",
#                         "price": "thirty five point four",
#                     },
#                 },
#             },
#         ),
#     ],
# ):
#     results = {
#         "item_id": item_id,
#         "item": item,
#     }
#     return results


# Partial update
@router.patch("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    stored_item_data = items[item_id]
    stored_item_model = Item(**stored_item_data)
    update_data = item.model_dump(exclude_unset=True)
    updated_item = stored_item_model.model_copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item


@router.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]


# @router.get(
#     "/items/{item_id}/public", response_model=Item, response_model_exclude=["tax"]
# )
# def read_item_public_data(item_id: str):
#     return items[item_id]


@router.post("/items/images/multiple")
async def create_multiple_images(images: list[Image]):
    return images


# response with arbitrary dict
@router.get("/keyword-weights/", response_model=dict[str, float])
async def read_keyword_weights():
    return {"foo": 2.3, "bar": 3.4}
