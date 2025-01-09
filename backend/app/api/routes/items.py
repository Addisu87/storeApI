# Routes for item operations
from typing import Annotated

from app.api.schemas.items import Item
from app.core.deps import get_token_header
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, UJSONResponse

from fastapi.templating import Jinja2Templates

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


fake_items_db = {"plumbus": {"title": "Plumbus"}, "gun": {"title": "Portal Gun"}}
tasks = {"foo": "Listen to the Bar Fighters"}

items = {
    "foo": {"title": "Fighters", "size": 6},
    "bar": {"title": "Tenders", "size": 3},
}

responses = {
    404: {"description": "Item not found"},
    302: {"description": "The item was moved"},
    403: {"description": "Not enough privileges"},
}


templates = Jinja2Templates(directory="templates")


@router.post(
    "/",
    response_model=Item,
    summary="Create an Item",
    status_code=status.HTTP_201_CREATED,
)
async def create_item(item: Item):
    """Create an item with all the information:
    - **title**: each item must have a title
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    \f
    :param item: User input.
    """  # noqa: D400
    # Additional status code
    # return JSONResponse(status_code=status.HTTP_201_CREATED, content=Item)
    return item


# Get items
@router.get("/", response_class=UJSONResponse, include_in_schema=False)
async def read_items():
    return [{"item_id": "Foo"}]


# Get individual item
@router.get(
    "/{item_id}",
    response_model=Item,
    responses={**responses, 200: {"content": {"image/png": {}}}},
)
async def read_item(request: Request, item_id: str, img: bool | None = None):
    if item_id not in fake_items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    elif img:
        return FileResponse("image.png", media_type="image/png")

    # return {"title": fake_items_db[item_id]["title"], "item_id": item_id}
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": item_id}
    )


# Update item
@router.put(
    "/{item_id}",
    tags=["custom"],
    responses={403: {"description": "Operation forbidden"}},
)
async def update_item(item_id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    return JSONResponse(content=json_compatible_item_data)
    # if item_id != "plumbus":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You can only update the item: plumbus",
    #     )
    # return {"item_id": item_id, "title": "The great Plumbus"}


@router.put("/{item_id}")
async def upsert_item(
    item_id: str,
    title: Annotated[str | None, Body()] = None,
    size: Annotated[int | None, Body()] = None,
):
    if item_id in items:
        item = items[item_id]
        item["title"] = title
        item["size"] = size
        return item
    else:
        item = {"title": title, "size": size}
        items[item_id] = item
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)


@router.put("/get-or-create-task/{item_id}", status_code=200)
def get_or_create_task(task_id: str, response: Response):
    if task_id not in tasks:
        tasks[task_id] = "This didn't exist before"
        response.status_code = status.HTTP_201_CREATED
    return tasks[task_id]


@router.post("/cookie")
def create_cookie():
    content = {"message": "Come to the dark side, we have cookies"}
    response = JSONResponse(content=content)
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return response
