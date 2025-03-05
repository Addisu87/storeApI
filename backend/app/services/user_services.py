# app/services/user_services.py
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.schemas import User, UserCreate, UserUpdate


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(session, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(session: Session, user_create: UserCreate) -> User:
    db_user = User(
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        full_name=user_create.full_name,
        is_active=True,  # Ensure active by default
        is_superuser=False,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(session: Session, db_user: User, user_in: UserUpdate) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    # Only update fields provided, don’t touch is_active unless specified
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
