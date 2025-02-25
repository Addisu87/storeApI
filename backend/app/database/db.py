from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import settings
from app.database import crud
from app.schemas.users import User, UserCreate

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
        user = crud.create_user(session=session, user_create=user_in)
