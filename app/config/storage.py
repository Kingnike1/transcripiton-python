"""
Storage configuration module.
Handles file storage settings and upload limits.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class StorageSettings(BaseSettings):
    """Storage-level settings."""

    STORAGE_PATH: str = Field(
        default="./storage",
        description="Root path for file storage"
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=500000000,
        description="Maximum upload size in bytes (500MB default)"
    )

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
