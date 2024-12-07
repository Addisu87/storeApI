# Pydantic models for user-related schemas

from pydantic import BaseModel, EmailStr


# Base user
class User(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    disabled: bool | None = None


# Inheritance
# Database model - have a hashed password
class UserInDB(User):
    hashed_password: str
