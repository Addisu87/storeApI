# User management services -
# CRUD for users, business logic
# Business logic related to authentication and authorization.


from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.schemas import User, UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create a new user.

    Args:
        session (Session): The database session.
        user_create (UserCreate): The user input data.

    Returns:
        User: The created user.

    """
    hashed_password = get_password_hash(user_create.password)
    user = User.model_validate(user_create, update={"hashed_password": hashed_password})
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """Update a user.

    Args:
        session (Session): The database session.
        user (User): The user to update.
        user_in (UserUpdate): The user input data.

    Returns:
        User: The updated user.

    """
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Retrieve a user by email.

    Args:
        session (Session): The database session.
        email (str): The email of the user to retrieve.

    Returns:
        User | None: The user if found, otherwise None.
    """
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate_user(*, session: Session, email: str, password: str) -> User | None:
    """Authenticate a user by email and password.

    Args:
        session (Session): The database session.
        email (str): The email of the user to authenticate.
        password (str): The password of the user to authenticate.

    Returns:
        User | None: The authenticated user if credentials are valid, otherwise None.
    """
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
