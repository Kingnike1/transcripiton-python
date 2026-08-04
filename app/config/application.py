"""
Application configuration module.
Handles core application settings like name, debug mode, host, and port.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class ApplicationSettings(BaseSettings):
    """Application-level settings."""

    APP_NAME: str = Field(default="AMIP", description="Application name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    SECRET_KEY: str = Field(default="secret", description="Secret key for security")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
