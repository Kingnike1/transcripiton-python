"""
Configuration package for AMIP.
Provides modularized settings for different concerns.
"""

from app.config.application import ApplicationSettings
from app.config.database import DatabaseSettings
from app.config.logging import LoggingSettings
from app.config.storage import StorageSettings
from app.config.audio import AudioSettings
from app.config.ai import AISettings
from app.config.security import SecuritySettings


class Settings:
    """Aggregated settings class combining all configuration modules.
    
    This class provides a unified interface to all application settings
    while maintaining modular organization internally.
    
    Example:
        >>> settings = Settings()
        >>> settings.app.DEBUG
        >>> settings.database.DATABASE_URL
        >>> settings.logging.LOG_LEVEL
    """

    def __init__(self):
        """Initialize all settings modules."""
        self.app = ApplicationSettings()
        self.database = DatabaseSettings()
        self.logging = LoggingSettings()
        self.storage = StorageSettings()
        self.audio = AudioSettings()
        self.ai = AISettings()
        self.security = SecuritySettings()

    # Convenience properties for backward compatibility
    @property
    def APP_NAME(self) -> str:
        """Get application name."""
        return self.app.APP_NAME

    @property
    def DEBUG(self) -> bool:
        """Get debug mode."""
        return self.app.DEBUG

    @property
    def SECRET_KEY(self) -> str:
        """Get secret key."""
        return self.app.SECRET_KEY

    @property
    def HOST(self) -> str:
        """Get server host."""
        return self.app.HOST

    @property
    def PORT(self) -> int:
        """Get server port."""
        return self.app.PORT

    @property
    def DATABASE_URL(self) -> str:
        """Get database URL."""
        return self.database.DATABASE_URL

    @property
    def LOG_LEVEL(self) -> str:
        """Get log level."""
        return self.logging.LOG_LEVEL

    @property
    def LOG_FILE(self) -> str:
        """Get log file path."""
        return self.logging.LOG_FILE

    @property
    def STORAGE_PATH(self) -> str:
        """Get storage path."""
        return self.storage.STORAGE_PATH

    @property
    def MAX_UPLOAD_SIZE(self) -> int:
        """Get maximum upload size."""
        return self.storage.MAX_UPLOAD_SIZE

    @property
    def WHISPER_MODEL(self) -> str:
        """Get Whisper model."""
        return self.audio.WHISPER_MODEL

    @property
    def WHISPER_LANGUAGE(self) -> str:
        """Get Whisper language."""
        return self.audio.WHISPER_LANGUAGE

    @property
    def PYANNOTE_MODEL(self) -> str:
        """Get pyannote model."""
        return self.audio.PYANNOTE_MODEL

    @property
    def PYANNOTE_DEVICE(self) -> str:
        """Get pyannote device."""
        return self.audio.PYANNOTE_DEVICE

    @property
    def OPENAI_API_KEY(self):
        """Get OpenAI API key."""
        return self.ai.OPENAI_API_KEY

    @property
    def OLLAMA_URL(self) -> str:
        """Get Ollama URL."""
        return self.ai.OLLAMA_URL

    @property
    def OLLAMA_MODEL(self) -> str:
        """Get Ollama model."""
        return self.ai.OLLAMA_MODEL


# Singleton instance
settings = Settings()
