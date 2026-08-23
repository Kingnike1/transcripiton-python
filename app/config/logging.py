"""Logging configuration."""

from pydantic import Field

from app.config.base import AMIPBaseSettings


class LoggingSettings(AMIPBaseSettings):
    """Logging and retention settings."""

    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: str = Field(
        default="./logs/amip.log",
        description="Path to the active AMIP technical log file",
    )
    LOG_MAX_BYTES: int = Field(
        default=10 * 1024 * 1024,
        gt=0,
        description="Rotate the active log after this many bytes (default: 10 MiB)",
    )
    LOG_BACKUP_COUNT: int = Field(
        default=5,
        ge=1,
        description="Number of rotated log files retained alongside the active log",
    )
