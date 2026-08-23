"""
Logging configuration module for AMIP.
Sets up structured file logging and a friendly console experience.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.config import settings


class FriendlyConsoleFormatter(logging.Formatter):
    """Render concise, human-friendly messages in the terminal."""

    _prefixes = {
        logging.DEBUG: "·",
        logging.INFO: "✓",
        logging.WARNING: "⚠",
        logging.ERROR: "✗",
        logging.CRITICAL: "✗",
    }

    def format(self, record: logging.LogRecord) -> str:
        prefix = self._prefixes.get(record.levelno, "→")
        message = record.getMessage()
        return f"{prefix} {message}"


class LoggerFactory:
    """Factory for creating consistently configured AMIP loggers."""

    # Keep technical detail in files. Later observability sprints will enrich it.
    _file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    _console_formatter = FriendlyConsoleFormatter()

    @classmethod
    def get_logger(
        cls,
        name: str,
        level: Optional[str] = None,
        console: bool = True,
        file: bool = True,
    ) -> logging.Logger:
        """Create and configure a logger instance."""
        logger = logging.getLogger(name)

        if level is None:
            level = settings.logging.LOG_LEVEL
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        logger.propagate = False

        # Clear existing handlers to avoid duplicate output on reload/import.
        logger.handlers.clear()

        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(cls._console_formatter)
            logger.addHandler(console_handler)

        if file:
            file_handler = cls._create_file_handler()
            file_handler.setFormatter(cls._file_formatter)
            logger.addHandler(file_handler)

        return logger

    @classmethod
    def _create_file_handler(cls) -> RotatingFileHandler:
        """Create the existing rotating technical file handler."""
        log_dir = os.path.dirname(settings.logging.LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        return RotatingFileHandler(
            settings.logging.LOG_FILE,
            maxBytes=settings.logging.LOG_MAX_BYTES,
            backupCount=settings.logging.LOG_BACKUP_COUNT,
            encoding="utf-8",
        )


def setup_logging() -> logging.Logger:
    """Configure the main AMIP logger for console and file output."""
    return LoggerFactory.get_logger(
        "amip",
        level=settings.logging.LOG_LEVEL,
        console=True,
        file=True,
    )


logger = setup_logging()
