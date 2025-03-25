# app/core/config.py
import secrets
from functools import lru_cache
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(value: Any) -> list[str] | str:
    if isinstance(value, str) and not value.startswith("["):
        return [i.strip() for i in value.split(",")]
    elif isinstance(value, list | str):
        return value
    raise ValueError(value)


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ENV_STATE: Literal["dev", "test", "prod"] = "dev"


class Settings(BaseConfig):
    # Databses
    DATABASE_URL: str | None = None

    # Security and API settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"

    # Admin credentials
    ADMIN_EMAIL: EmailStr
    ADMIN_PASSWORD: str

    # CORS and frontend
    FRONTEND_HOST: str = "http://localhost:5173"
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl], BeforeValidator(parse_cors)] = []

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin) for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    # Project metadata
    PROJECT_NAME: str = "Full Stack FastAPI Project"

    SENTRY_DSN: HttpUrl | None = None
    LOGTAIL_API_KEY: str | None = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "storeapi"
    POSTGRES_PASSWORD: str = "storeapi87"
    POSTGRES_DB: str = "storeapidb"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    def get_db_uri_string(self) -> str:
        """Return SQLALCHEMY_DATABASE_URI as a string for SQLAlchemy."""
        return str(self.SQLALCHEMY_DATABASE_URI)

    # FastAPI-Mail configuration
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_FROM_NAME: str | None = None  # Optional
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.example.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = True
    EMAILS_ENABLED: bool = True


class DevConfig(Settings):
    model_config = SettingsConfigDict(env_prefix="DEV_", extra="ignore")


class ProdConfig(Settings):
    model_config = SettingsConfigDict(env_prefix="PROD_", extra="ignore")


class TestConfig(Settings):
    model_config = SettingsConfigDict(env_prefix="TEST_", extra="ignore")

    # Database settings
    POSTGRES_USER: str = "storeapi"
    POSTGRES_PASSWORD: str = "storeapi87"
    POSTGRES_DB: str = "testdb"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    DB_FORCE_ROLL_BACK: bool = True

    # Admin credentials for testing
    ADMIN_EMAIL: EmailStr = "admin@test.com"
    ADMIN_PASSWORD: str = "testadminpass"

    # Email settings for testing
    MAIL_USERNAME: str = "test_user"
    MAIL_PASSWORD: str = "test_pass"
    MAIL_FROM: EmailStr = "test@example.com"
    MAIL_SERVER: str = "localhost"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = False
    EMAILS_ENABLED: bool = False  # Disable actual email sending in tests


# Cache the settings
@lru_cache
def get_settings(env_state: str = BaseConfig().ENV_STATE):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


settings = get_settings()  # Default to BaseConfig().ENV_STATE ("dev")
