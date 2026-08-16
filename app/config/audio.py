"""
Audio configuration module.
Handles audio processing settings (inspection, transcription, speaker identification).
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class AudioSettings(BaseSettings):
    """Audio processing settings."""

    FFPROBE_BINARY: str = Field(
        default="ffprobe",
        description="ffprobe executable name or path used for media inspection",
    )
    FFPROBE_TIMEOUT_SECONDS: int = Field(
        default=15,
        ge=1,
        description="Maximum ffprobe inspection time per upload",
    )

    WHISPER_MODEL: str = Field(
        default="base",
        description="Whisper model size (tiny, base, small, medium, large)",
    )
    WHISPER_LANGUAGE: str = Field(
        default="auto",
        description="Whisper language (auto-detect or specific language code)",
    )

    PYANNOTE_MODEL: str = Field(
        default="pyannote/speaker-diarization-3.1",
        description="pyannote model identifier",
    )
    PYANNOTE_DEVICE: str = Field(
        default="cpu",
        description="Device for pyannote (cpu or cuda)",
    )

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
