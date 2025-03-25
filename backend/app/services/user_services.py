# app/services/user_services.py
import logging
import uuid

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.user_models import User, UserCreate, UserUpdate

logger = logging.getLogger(__name__)


def get_user_by_email(session: Session, email: str) -> User | None:
    """Retrieve a user by their email address."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user(session: Session, user_id: uuid.UUID) -> User | None:
    """Retrieve a user by their ID."""
    return session.get(User, user_id)


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    """Authenticate a user by email and password."""
    logger.debug(f"Authenticating user with email: {email}")
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        logger.debug(f"User not found: {email}")
        return None
    if not verify_password(password, user.hashed_password):
        logger.debug(f"Password verification failed for user: {email}")
        return None
    if not user.is_active:
        logger.debug(f"User {email} is not active")
        return None
    logger.debug(f"User authenticated successfully: {email}")
    return user


def create_user(session: Session, *, user_create: UserCreate) -> User:
    """Create a new user."""
    db_user = User(
        email=user_create.email,
        full_name=user_create.full_name,
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
        hashed_password=get_password_hash(user_create.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(session: Session, *, db_user: User, user_in: UserUpdate) -> User:
    """Update user attributes."""
    user_data = user_in.model_dump(exclude_unset=True)
    if user_data.get("password"):
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

    for field, value in user_data.items():
        setattr(db_user, field, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
