"""Storage and upload-limit configuration."""

from pydantic import Field

from app.config.base import AMIPBaseSettings


class StorageSettings(AMIPBaseSettings):
    """Storage-level settings."""

    STORAGE_PATH: str = Field(
        default="./storage",
        description="Root path for file storage",
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=500_000_000,
        gt=0,
        description="Maximum upload size in bytes",
    )
