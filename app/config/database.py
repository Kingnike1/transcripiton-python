"""Database connection configuration."""

from pydantic import Field

from app.config.base import AMIPBaseSettings


class DatabaseSettings(AMIPBaseSettings):
    """Database-level settings."""

    DATABASE_URL: str = Field(
        default="sqlite:///./app.db",
        description="Database connection URL",
    )
    DB_POOL_SIZE: int = Field(default=5, ge=1, le=50)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=100)
    DB_POOL_RECYCLE_SECONDS: int = Field(default=1800, ge=60)
    DB_CONNECT_TIMEOUT_SECONDS: int = Field(default=10, ge=1, le=60)
