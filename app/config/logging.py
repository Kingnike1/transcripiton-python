"""Logging configuration."""

from pydantic import Field

from app.config.base import AMIPBaseSettings


class LoggingSettings(AMIPBaseSettings):
    """Logging-level settings."""

    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level",
    )
    LOG_FILE: str = Field(
        default="./logs/app.log",
        description="Path to the rotating log file",
    )
    LOG_MAX_BYTES: int = Field(
        default=10 * 1024 * 1024,
        gt=0,
        description="Maximum log file size in bytes",
    )
    LOG_BACKUP_COUNT: int = Field(
        default=5,
        ge=0,
        description="Number of backup log files to keep",
    )
