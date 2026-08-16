"""Database connection configuration."""

from pydantic import Field

from app.config.base import AMIPBaseSettings


class DatabaseSettings(AMIPBaseSettings):
    """Database-level settings."""

    DATABASE_URL: str = Field(
        default="sqlite:///./app.db",
        description="Database connection URL",
    )
