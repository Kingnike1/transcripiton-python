"""
Security configuration module.
Handles security-related settings (CORS, authentication, etc.).
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class SecuritySettings(BaseSettings):
    """Security-related settings."""

    # Future: Add CORS, authentication, and other security settings
    # This module is prepared for future security implementations
    # without requiring architectural changes

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
