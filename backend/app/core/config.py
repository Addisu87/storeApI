import secrets
from functools import lru_cache
from typing import Literal

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV_STATE: Literal["dev", "prod", "test"] = "dev"


class Settings(BaseConfig):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""


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
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


setting = get_config(BaseConfig().ENV_STATE)
