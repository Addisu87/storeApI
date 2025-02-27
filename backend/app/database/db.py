from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import settings
from app.core.logging_config import logger
from app.models.users import User, UserCreate
from app.services import user_services

print(settings.SQLALCHEMY_DATABASE_URL)

# Create an Engine
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URL))


# make sure all SQLModel models are imported (app.) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
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
