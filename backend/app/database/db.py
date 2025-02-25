from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import settings
from app.schemas.users import User, UserCreate
from app.services import user_services

# Create an Engine
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    SQLModel.metadata.create_all(engine)

    user = session.exec(select(User).where(User.email == settings.ADMIN_EMAIL)).first()

    if not user:
        user_in = UserCreate(
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            is_superuser=True,
        )
        user = user_services.create_user(session=session, user_create=user_in)
