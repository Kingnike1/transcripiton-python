"""Audio inspection and processing configuration."""

from pydantic import Field

from app.config.base import AMIPBaseSettings


class AudioSettings(AMIPBaseSettings):
    """Audio processing and local speech-to-text settings."""

    FFPROBE_BINARY: str = Field(default="ffprobe", description="ffprobe executable name or path")
    FFPROBE_TIMEOUT_SECONDS: int = Field(default=15, ge=1)
    WHISPER_MODEL: str = Field(default="base")
    WHISPER_LANGUAGE: str = Field(default="auto")
    WHISPER_DEVICE: str = Field(default="cpu")
    WHISPER_COMPUTE_TYPE: str = Field(default="int8")
    WHISPER_BEAM_SIZE: int = Field(default=5, ge=1, le=10)
    WHISPER_VAD_FILTER: bool = Field(default=True)
    PYANNOTE_MODEL: str = Field(
        default="pyannote/speaker-diarization-community-1",
        description="pyannote speaker diarization model identifier",
    )
    PYANNOTE_DEVICE: str = Field(default="cpu", description="Device for pyannote (cpu or cuda)")
