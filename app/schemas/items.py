#
from fastapi import (
    APIRouter,
    Query,
    Body,
    Cookie,
    Header,
    status,
    HTTPException,
    Depends,
)


from pydantic import BaseModel, Field, HttpUrl

from datetime import datetime

# from api.dependencies.common_query import (
#     CommonQueryParams,
#     query_or_cookie_extractor,
# )


# from app.routers.users import User

router = APIRouter(prefix="", tags=["items"])

fake_db = {}


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
    timestamp: datetime
    description: str | None = Field(
        default=None,
        title="The description of the item",
        max_length=300,
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    # tax: float | None = None
    tax: float = 10.5
    # set types - unique items
    # tags: set[str] = set()
    tags: list[str] = []
    summary: str | None = Field(default=None, title="Item summary", max_length=300)

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
