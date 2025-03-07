import random
import string

from sqlmodel import Session

from app.models.item_models import Item, ItemCreate
from app.models.user_models import User, UserCreate
from app.services.item_services import create_item
from app.services.user_services import create_user


def random_lower_string() -> str:
    """Generate a random string of lowercase letters."""
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    """Generate a random email address."""
    return f"{random_lower_string()}@{random_lower_string()}.com"


def create_random_user(db: Session) -> tuple[User, str]:
    """Create a random user."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)
    return user, password


def create_random_item(db: Session, owner: User | None = None) -> Item:
    """Create a random item."""
    if owner is None:
        owner, _ = create_random_user(db)
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    return create_item(session=db, item_in=item_in, owner_id=owner.id)


def override_current_user(user: User):
    """Override the current user dependency."""

    def _override():
        return user

    return _override
