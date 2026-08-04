"""
Core configuration module for AMIP.
Handles environment variables and application settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "AMIP"
    DEBUG: bool = False
    SECRET_KEY: str = "secret"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"

    # Transcription
    WHISPER_MODEL: str = "base"
    WHISPER_LANGUAGE: str = "auto"

    # Speaker Identification
    PYANNOTE_MODEL: str = "pyannote/speaker-diarization-3.1"
    PYANNOTE_DEVICE: str = "cpu"

    # Storage
    STORAGE_PATH: str = "./storage"
    MAX_UPLOAD_SIZE: int = 500000000  # 500MB

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


# Singleton instance
settings = Settings()
