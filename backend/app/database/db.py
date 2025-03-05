import logging

from sqlmodel import Session, select

from app.core.config import settings
from app.models.schemas import User, UserCreate
from app.services.user_services import create_user

logger = logging.getLogger(__name__)


# make sure all SQLModel models are imported (app.models.schemas) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly


def init_db(session: Session) -> None:
    """Initialize the database and ensure the admin user exists."""
    try:
        # Test the database connection
        session.exec(select(1))
        logger.info("Database connection successful")

        # Check if the admin user exists
        user = session.exec(
            select(User).where(User.email == settings.ADMIN_EMAIL)
        ).first()
        logger.debug(
            f"Fetching user with email: {settings.ADMIN_EMAIL}, found user: {user}"
        )

        if not user:
            user_in = UserCreate(
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                is_superuser=True,
            )
            user = create_user(session=session, user_create=user_in)
            logger.info(f"Admin user created: {user}")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise e
