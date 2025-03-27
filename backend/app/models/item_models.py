from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


# Forward reference for User (to avoid circular imports)
class User(SQLModel):
    id: UUID


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)


# Database model
class Item(ItemBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: UUID = Field(foreign_key="user.id", nullable=False)
    owner: "User" = Relationship(back_populates="items")


# Properties to return via API
class ItemPublic(ItemBase):
    id: UUID
    owner_id: UUID


class ItemsPublic(BaseModel):
    data: List[ItemPublic]
    count: int
