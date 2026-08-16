"""Alembic environment for AMIP database migrations."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import settings
from app.database.base import Base
import app.models  # noqa: F401 - registers all mapped models in Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Runtime configuration is the source of truth. The URL in alembic.ini is only
# a safe local fallback for tooling that inspects the file without importing app.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


def _configure(connection=None) -> None:
    """Configure Alembic consistently for SQLite and future PostgreSQL usage."""
    url = config.get_main_option("sqlalchemy.url")
    kwargs = {
        "target_metadata": target_metadata,
        "compare_type": True,
        "render_as_batch": url.startswith("sqlite"),
    }

    if connection is None:
        context.configure(
            url=url,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            **kwargs,
        )
    else:
        context.configure(connection=connection, **kwargs)


def run_migrations_offline() -> None:
    """Run migrations without creating an Engine."""
    _configure()
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        _configure(connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
