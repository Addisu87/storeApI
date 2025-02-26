import secrets
from functools import lru_cache
from typing import Literal

from pydantic import HttpUrl, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV_STATE: Literal["dev", "prod", "test"] = "dev"


class Settings(BaseConfig):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    # 60 minutes * 24 hours * 7 days = 7 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    FRONTEND_HOST: str = "http://localhost:5173"

    PROJECT_NAME: str | None = None
    SENTRY_DSN: HttpUrl | None = None
    POSTGRES_SERVER: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


class DevConfig(Settings):  # noqa: D101
    model_config = SettingsConfigDict(env_prefix="DEV_", extra="ignore")


class ProdConfig(Settings):  # noqa: D101
    model_config = SettingsConfigDict(env_prefix="PROD_", extra="ignore")


class TestConfig(Settings):  # noqa: D101
    model_config = SettingsConfigDict(env_prefix="TEST_", extra="ignore")

    DATABASE_URL: str = "postgresql://username:password@localhost/testdb"
    DB_FORCE_ROLL_BACK: bool = True


# lets to avoid reading the dotenv file again and again for each request
@lru_cache
def get_settings(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


settings = get_settings(BaseConfig().ENV_STATE)
