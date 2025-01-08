# Pydantic models for item-related schemas
# Data validation, Data serialization, Data documentation
from dataclasses import dataclass, field
from datetime import datetime

from pydantic import BaseModel


@dataclass
class Item(BaseModel):  # noqa: D101
    title: str
    price: float
    tags: list[str] = field(default_factory=list)
    description: str | None = None
    tax: float | None = None
    timestamp: datetime
