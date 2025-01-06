# Pydantic models for item-related schemas
from datetime import datetime
from typing import List, Union

from pydantic import BaseModel


class Item(BaseModel):
    title: str
    description: Union[str, None] = None
    price: float
    tax: float | None = None
    # tags: Set[str] = set()
    tags: List[str]
    timestamp: datetime
