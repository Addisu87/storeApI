# user-related Pydantic model

from pydantic import BaseModel, EmailStr


# Base user
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


# Input model- Inheritance
class UserIn(UserBase):
    password: str


# Output model
class UserOut(UserBase):
    pass


# Database model - have a hashed password
class UserInDB(UserBase):
    hashed_password: str
