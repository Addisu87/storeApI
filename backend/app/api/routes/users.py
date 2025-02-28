# Routes for user operations
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from app.core.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models.schemas import Item, Message, User, UserCreate, UserPublic, UserUpdate

router = APIRouter(prefix="", tags=["users"])


# Create a user -
# ensure data is validated and serialized correctly(response_model)
@router.post("/users/", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# Read users - ensure data is validated and serialized correctly
@router.get("/users/", response_model=list[UserPublic])
def read_users(
    session: SessionDep,
    skip: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Any:
    """Retrives users.

    Args:
        session (SessionDep): _description_
        offset (int, optional): _description_. Defaults to 0.
        limit (Annotated[int, Query, optional): _description_. Defaults to 100)]=100.

    Returns:
        Any: _description_
    """
    count_statment = select(func.count()).select_from(User)
    count = session.exec(count_statment).one()

    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return UserPublic(data=users, count=count)


# Read user by Id
@router.get("/users/{user_id}", response_model=UserPublic)
def read_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    return user


# Update user by Id
@router.patch("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user: UserUpdate, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    # only the data sent by the client
    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


# Delete user
@router.delete("/users/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    user_id: uuid.UUID, current_user: CurrentUser, session: SessionDep
) -> Message:
    """_summary_

    Args:
        user_id (uuid.UUID): _description_
        current_user (CurrentUser): _description_
        session (SessionDep): _description_

    Raises:
        HTTPException: user not found

    Returns:
        Message: User deleted successfully
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    if user == current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves",
        )
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
