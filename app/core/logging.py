"""
Logging configuration module for AMIP.
Sets up structured logging with file and console handlers.
Supports separate log levels for different components.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.config import settings


class LoggerFactory:
    """Factory for creating configured logger instances.
    
    Provides methods to create loggers with consistent formatting
    and handler configuration across the application.
    """

    # Shared formatter
    _formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    @classmethod
    def get_logger(
        cls,
        name: str,
        level: Optional[str] = None,
        console: bool = True,
        file: bool = True,
    ) -> logging.Logger:
        """Create and configure a logger instance.
        
        Args:
            name: Logger name (typically __name__)
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console: Whether to add console handler
            file: Whether to add file handler
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        
        # Set log level
        if level is None:
            level = settings.logging.LOG_LEVEL
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Add console handler
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(cls._formatter)
            logger.addHandler(console_handler)
        
        # Add file handler
        if file:
            file_handler = cls._create_file_handler()
            file_handler.setFormatter(cls._formatter)
            logger.addHandler(file_handler)
        
        return logger

    @classmethod
    def _create_file_handler(cls) -> RotatingFileHandler:
        """Create a rotating file handler.
        
        Returns:
            Configured RotatingFileHandler
        """
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(settings.logging.LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        handler = RotatingFileHandler(
            settings.logging.LOG_FILE,
            maxBytes=settings.logging.LOG_MAX_BYTES,
            backupCount=settings.logging.LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        return handler


def setup_logging() -> logging.Logger:
    """Configure application logging.
    
    Sets up the main logger with both console and file handlers.
    Uses rotation for file handler to manage log file size.
    
    Returns:
        Configured logger instance
    """
    return LoggerFactory.get_logger(
        "amip",
        level=settings.logging.LOG_LEVEL,
        console=True,
        file=True,
    )


# Initialize logger when module is imported
logger = setup_logging()
