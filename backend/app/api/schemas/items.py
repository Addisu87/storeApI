# Pydantic models for item-related schemas
from typing import Set

from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: Set[str] = set()
