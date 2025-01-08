# Global app configuration settings

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):  # noqa: D101
    project_name: str = "Full Stack FastAPI Project"
    admin_email: str
    items_per_user: int = 50

    model_config = SettingsConfigDict(env_file=".env")
