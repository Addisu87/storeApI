import random
import string
import uuid
from typing import Dict

from sqlmodel import Session

from app.models.item_models import Item
from app.models.user_models import User, UserCreate
from app.services.user_services import create_user


def random_lower_string(length: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_uuid() -> uuid.UUID:
    return uuid.uuid4()


def create_random_user(session: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        email=email,
        password=password,
        full_name=random_lower_string(),
    )
    user = create_user(session=session, user_create=user_in)
    return user


def create_random_item(session: Session, owner_id: uuid.UUID) -> Item:
    item = Item(
        title=random_lower_string(),
        description=random_lower_string(),
        owner_id=owner_id,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def user_authentication_headers(*, client, email: str, password: str) -> Dict[str, str]:
    data = {"username": email, "password": password}
    response = client.post("/api/v1/auth/login", data=data)
    auth_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {auth_token}"}
