"""Aggregated configuration for AMIP."""

from typing import Optional

from app.config.ai import AISettings
from app.config.application import ApplicationSettings
from app.config.audio import AudioSettings
from app.config.database import DatabaseSettings
from app.config.logging import LoggingSettings
from app.config.security import SecuritySettings
from app.config.storage import StorageSettings


class Settings:
    """Expose modular settings through one backwards-compatible interface."""

    def __init__(self) -> None:
        """Load all configuration modules from the current environment."""
        self.app = ApplicationSettings()
        self.database = DatabaseSettings()
        self.logging = LoggingSettings()
        self.storage = StorageSettings()
        self.audio = AudioSettings()
        self.ai = AISettings()
        self.security = SecuritySettings()

    @property
    def APP_NAME(self) -> str:
        return self.app.APP_NAME

    @property
    def ENVIRONMENT(self) -> str:
        return self.app.ENVIRONMENT

    @property
    def DEBUG(self) -> bool:
        return self.app.DEBUG

    @property
    def SECRET_KEY(self) -> str:
        return self.app.SECRET_KEY

    @property
    def HOST(self) -> str:
        return self.app.HOST

    @property
    def PORT(self) -> int:
        return self.app.PORT

    @property
    def DATABASE_URL(self) -> str:
        return self.database.DATABASE_URL

    @property
    def LOG_LEVEL(self) -> str:
        return self.logging.LOG_LEVEL

    @property
    def LOG_FILE(self) -> str:
        return self.logging.LOG_FILE

    @property
    def STORAGE_PATH(self) -> str:
        return self.storage.STORAGE_PATH

    @property
    def MAX_UPLOAD_SIZE(self) -> int:
        return self.storage.MAX_UPLOAD_SIZE

    @property
    def WHISPER_MODEL(self) -> str:
        return self.audio.WHISPER_MODEL

    @property
    def WHISPER_LANGUAGE(self) -> str:
        return self.audio.WHISPER_LANGUAGE

    @property
    def PYANNOTE_MODEL(self) -> str:
        return self.audio.PYANNOTE_MODEL

    @property
    def PYANNOTE_DEVICE(self) -> str:
        return self.audio.PYANNOTE_DEVICE

    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        return self.ai.OPENAI_API_KEY

    @property
    def OLLAMA_URL(self) -> str:
        return self.ai.OLLAMA_URL

    @property
    def OLLAMA_MODEL(self) -> str:
        return self.ai.OLLAMA_MODEL


settings = Settings()
