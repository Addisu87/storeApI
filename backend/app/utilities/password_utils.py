import logging
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_password_reset_token(email: str) -> str:
    logger.debug("Creating password reset token", extra={"email": email})
    expire = datetime.now(timezone.utc) + timedelta(
        hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS
    )
    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(
        jwt_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    logger.debug("Verifying password reset token", extra={"token": token})
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None
