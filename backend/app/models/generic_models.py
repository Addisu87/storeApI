# generic_models.py
from sqlmodel import SQLModel


# Generic message model
class Message(SQLModel):
    message: str
