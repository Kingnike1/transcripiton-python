"""Audio inspection and processing configuration."""

from pydantic import Field

from app.config.base import AMIPBaseSettings


class AudioSettings(AMIPBaseSettings):
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
        description="Whisper model identifier",
    )
    WHISPER_LANGUAGE: str = Field(
        default="auto",
        description="Whisper language or auto-detect",
    )
    PYANNOTE_MODEL: str = Field(
        default="pyannote/speaker-diarization-3.1",
        description="pyannote model identifier",
    )
    PYANNOTE_DEVICE: str = Field(
        default="cpu",
        description="Device for pyannote (cpu or cuda)",
    )
