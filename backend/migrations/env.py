# migrations/env.py
from logging.config import fileConfig

from alembic import context

# Import your settings
from app.core.config import settings

# Import all models via the app.models module to register their metadata
from app.models import Item, User  # Explicit imports from __init__.py
from sqlalchemy import engine_from_config, pool

# Import SQLModel base
from sqlmodel import SQLModel

# Alembic Config object
config = context.config

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata
target_metadata = SQLModel.metadata

# Ensure models are "used" to prevent Ruff from removing imports
# This is a minimal no-op to satisfy linters
model_registry = [User, Item]  # Reference the imports

# Dynamically set the SQLAlchemy URL from settings
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
