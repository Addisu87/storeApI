# app/services/user_services.py
import logging

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.schemas import User, UserCreate, UserUpdate

logger = logging.getLogger(__name__)


def get_user_by_email(session: Session, email: str) -> User | None:
    """Retrieve a user by their email address."""
    return session.exec(select(User).where(User.email == email)).first()


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
    logger.debug(f"User authenticated successfully: {email}")
    return user


def create_user(session: Session, user_create: UserCreate) -> User:
    """Create a new user."""
    logger.debug(f"Creating user with email: {user_create.email}")
    db_user = User(
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
        full_name=user_create.full_name,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(session: Session, db_user: User, user_in: UserUpdate) -> User:
    """Update an existing user in the database."""
    user_data = user_in.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
