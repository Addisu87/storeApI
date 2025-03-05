from logging.config import fileConfig

from alembic import context
from app.core.config import settings
from app.models.schemas import SQLModel
from sqlalchemy import engine_from_config, pool

# Alembic Config object, which provides access to values within the .ini file
config = context.config

# Set up logging from the config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata to SQLModel.metadata (all your models should inherit from SQLModel)
target_metadata = SQLModel.metadata


if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings.get_db_uri_string())


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {})
    if not configuration:
        raise ValueError(
            f"Configuration section '{config.config_ini_section}' not found in config file."
        )
    sqlalchemy_url = config.get_main_option("sqlalchemy.url")
    if sqlalchemy_url is None:
        raise ValueError("sqlalchemy.url is not set in the configuration.")
    configuration["sqlalchemy.url"] = sqlalchemy_url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
