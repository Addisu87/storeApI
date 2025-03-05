import random
import string

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models.schemas import Item, ItemCreate, User, UserCreate
from app.services.item_services import create_item
from app.services.user_services import create_user


def random_lower_string() -> str:
    """Generate a random string of lowercase letters."""
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    """Generate a random email address."""
    return f"{random_lower_string()}@{random_lower_string()}.com"


def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Get authorization headers for a normal user."""
    # Use fixture credentials directly
    data = {"username": "user@example.com", "password": "usersecret"}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    assert r.status_code == 200, f"Login failed: {r.text}"
    response = r.json()
    auth_token = response["access_token"]
    return {"Authorization": f"Bearer {auth_token}"}


def create_random_user(db: Session) -> User:
    """Create a random user."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    return create_user(session=db, user_create=user_in)


def create_random_item(db: Session, owner: User | None = None) -> Item:
    """Create a random item."""
    if owner is None:
        owner = create_random_user(db)
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    return create_item(session=db, item_in=item_in, owner_id=owner.id)


def override_current_user(user: User):
    """Override the current user dependency."""

    def _override():
        return user

    return _override
