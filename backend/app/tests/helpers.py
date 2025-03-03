import random
import string

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models.schemas import Item, ItemCreate, User, UserCreate, UserUpdate
from app.services.item_services import create_item
from app.services.user_services import create_user, get_user_by_email, update_user


def random_lower_string() -> str:
    """Generate a random string of lowercase letters."""
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    """Generate a random email address."""
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    """Get authorization headers for the superuser."""
    login_data = {"username": settings.ADMIN_USER, "password": settings.ADMIN_PASSWORD}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    """Get authorization headers for a user."""
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> User:
    """Create a random user."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)
    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """Return a valid token for the user with given email.
    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = get_user_by_email(session=db, email=email)
    if not user:
        user_in_create = UserCreate(email=email, password=password)
        user = create_user(session=db, user_create=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        if not user.id:
            raise Exception("User id not set")
        user = update_user(session=db, db_user=user, user_in=user_in_update)
    return user_authentication_headers(client=client, email=email, password=password)


def create_random_items(db: Session) -> Item:
    """Create random items."""
    user = create_random_user(db)
    owner_id = user.id

    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    return create_item(session=db, item_in=item_in, owner_id=owner_id)
