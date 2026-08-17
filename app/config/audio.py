"""Audio inspection and processing configuration."""

from pydantic import Field

from app.config.base import AMIPBaseSettings


class AudioSettings(AMIPBaseSettings):
    """Audio processing and local speech-to-text settings."""

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
        description="faster-whisper model identifier for the internal MVP",
    )
    WHISPER_LANGUAGE: str = Field(
        default="auto",
        description="Language code or auto-detect",
    )
    WHISPER_DEVICE: str = Field(
        default="cpu",
        description="faster-whisper execution device (cpu or cuda)",
    )
    WHISPER_COMPUTE_TYPE: str = Field(
        default="int8",
        description="CTranslate2 compute type; int8 is the safe CPU default",
    )
    WHISPER_BEAM_SIZE: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Beam size used during transcription",
    )
    WHISPER_VAD_FILTER: bool = Field(
        default=True,
        description="Enable faster-whisper VAD filtering",
    )
    PYANNOTE_MODEL: str = Field(
        default="pyannote/speaker-diarization-3.1",
        description="pyannote model identifier",
    )
    PYANNOTE_DEVICE: str = Field(
        default="cpu",
        description="Device for pyannote (cpu or cuda)",
    )
