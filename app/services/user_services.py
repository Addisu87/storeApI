# User management services -
# CRUD for users, business logic
# Business logic related to authentication and authorization.

from app.schemas.users import UserInDB
from app.core.security import verify_password


# get user using username at db
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
