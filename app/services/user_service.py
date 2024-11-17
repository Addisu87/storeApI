# User management services -
# User-related business logic

from app.schemas.users import UserIn, UserInDB


# Decode token
def fake_decode_token(token):
    return UserIn(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )


# hashed password
def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


# save user to db
def fake_save_user(user_in: UserIn) -> UserInDB:
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db
