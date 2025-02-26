from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.users import User, UserCreate
from app.services import user_services

print(settings.SQLALCHEMY_DATABASE_URL)

# Create an Engine
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URL))


def init_db(session: Session) -> None:
    SQLModel.metadata.create_all(engine)
    user = session.exec(select(User).where(User.email == settings.ADMIN_EMAIL)).first()
    logger.debug(
        f"Fetching user with email: {settings.ADMIN_EMAIL}, found user: {user}"
    )

    if not user:
        logger.debug(
            f"No user found with email: {settings.ADMIN_EMAIL}, creating new user."
        )
        user_in = UserCreate(
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            is_superuser=True,
        )
        user = user_services.create_user(session=session, user_create=user_in)
