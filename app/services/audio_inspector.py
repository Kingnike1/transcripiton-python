"""Audio container inspection backed by ffprobe."""

from dataclasses import dataclass
import json
import logging
from pathlib import Path
import shutil
import subprocess
from typing import Optional, Protocol

from app.exceptions.audio import AudioFormatError, AudioInspectorUnavailableError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AudioMediaMetadata:
    """Normalized technical metadata extracted from an audio container."""

    duration_seconds: Optional[float]
    codec_name: Optional[str]
    channels: Optional[int]
    sample_rate: Optional[int]


class AudioInspector(Protocol):
    """Contract for media metadata inspection."""

    def inspect(self, path: Path) -> AudioMediaMetadata:
        """Inspect one staged audio file."""
        ...


class FFprobeAudioInspector:
    """Inspect uploaded media without decoding it inside the web process."""

    def __init__(self, binary: str = "ffprobe", timeout_seconds: int = 15) -> None:
        self.binary = binary
        self.timeout_seconds = timeout_seconds

    def inspect(self, path: Path) -> AudioMediaMetadata:
        """Return media metadata or reject malformed/non-audio containers."""
        resolved_binary = shutil.which(self.binary)
        if resolved_binary is None:
            raise AudioInspectorUnavailableError(
                "Audio inspection is unavailable because ffprobe is not installed"
            )

        command = [
            resolved_binary,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_name,codec_type,channels,sample_rate,duration",
            "-of",
            "json",
            str(path),
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise AudioFormatError("Audio inspection timed out") from exc

        if result.returncode != 0:
            logger.warning("ffprobe rejected uploaded media: %s", result.stderr.strip())
            raise AudioFormatError("Uploaded file is not a readable audio container")

        try:
            payload = json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise AudioFormatError("Audio inspection returned invalid metadata") from exc

        streams = payload.get("streams") or []
        audio_stream = next(
            (stream for stream in streams if stream.get("codec_type") == "audio"),
            None,
        )
        if audio_stream is None:
            raise AudioFormatError("Uploaded media does not contain an audio stream")

        format_data = payload.get("format") or {}
        duration_value = format_data.get("duration") or audio_stream.get("duration")

        return AudioMediaMetadata(
            duration_seconds=self._optional_float(duration_value),
            codec_name=audio_stream.get("codec_name"),
            channels=self._optional_int(audio_stream.get("channels")),
            sample_rate=self._optional_int(audio_stream.get("sample_rate")),
        )

    @staticmethod
    def _optional_float(value: object) -> Optional[float]:
        if value in (None, "", "N/A"):
            return None
        if not isinstance(value, (str, int, float)):
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _optional_int(value: object) -> Optional[int]:
        if value in (None, "", "N/A"):
            return None
        if not isinstance(value, (str, int, float)):
            return None
        try:
            return int(value)
        except ValueError:
            return None
