"""
Logging configuration module.
Handles logging settings and log file management.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):
    """Logging-level settings."""

    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    LOG_FILE: str = Field(
        default="./logs/app.log",
        description="Path to log file"
    )
    LOG_MAX_BYTES: int = Field(
        default=10 * 1024 * 1024,
        description="Maximum log file size in bytes (10MB default)"
    )
    LOG_BACKUP_COUNT: int = Field(
        default=5,
        description="Number of backup log files to keep"
    )

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
