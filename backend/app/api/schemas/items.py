# Pydantic models for item-related schemas
from pydantic import BaseModel


class Item(BaseModel):
    id: str
    title: str
    description: str | None = None