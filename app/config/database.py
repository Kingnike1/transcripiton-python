"""
Database configuration module.
Handles database connection settings and ORM configuration.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database-level settings."""

    DATABASE_URL: str = Field(
        default="sqlite:///./app.db",
        description="Database connection URL"
    )

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
