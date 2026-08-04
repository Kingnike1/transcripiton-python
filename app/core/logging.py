"""
Logging configuration module for AMIP.
Sets up structured logging with file and console handlers.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure application logging.
    
    Sets up a logger with both console and file handlers.
    Uses rotation for file handler to manage log file size.
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

    # Get root logger
    logger = logging.getLogger("amip")
    
    # Set log level
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Initialize logger when module is imported
logger = setup_logging()
