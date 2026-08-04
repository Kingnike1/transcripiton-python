"""
Audio configuration module.
Handles audio processing settings (transcription, speaker identification).
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class AudioSettings(BaseSettings):
    """Audio processing settings."""

    # Transcription settings
    WHISPER_MODEL: str = Field(
        default="base",
        description="Whisper model size (tiny, base, small, medium, large)"
    )
    WHISPER_LANGUAGE: str = Field(
        default="auto",
        description="Whisper language (auto-detect or specific language code)"
    )

    # Speaker identification settings
    PYANNOTE_MODEL: str = Field(
        default="pyannote/speaker-diarization-3.1",
        description="pyannote model identifier"
    )
    PYANNOTE_DEVICE: str = Field(
        default="cpu",
        description="Device for pyannote (cpu or cuda)"
    )

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
