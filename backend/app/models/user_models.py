from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.item_models import Item


# Shared properties
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    is_active: bool = True
    is_superuser: bool = False


# Properties to receive via API on registration
class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Database model
class User(UserBase, table=True):
    """Use string-based forward reference"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    items: list["Item"] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"cascade": "delete"}
    )


# Properties to return via API
class UserPublic(UserBase):
    id: UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Properties to receive via API on update
class UserUpdate(SQLModel):
    email: str | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None


class UserUpdateMe(SQLModel):
    email: str | None = None
    full_name: str | None = None
    password: str | None = None
