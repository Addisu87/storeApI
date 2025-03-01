# Tests for security logic

from datetime import timedelta

import jwt

from app.core.config import settings
from app.core.security import create_access_token


def test_create_access_token():
    token = create_access_token(
        "1234", expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    assert {"sub": "1234"}.items() <= jwt.decode(
        token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    ).items()


