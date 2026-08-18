"""Validation rules for uploaded audio files."""

from pathlib import Path
from typing import Mapping

from app.config import settings
from app.exceptions.audio import AudioFormatError, AudioUploadError


class AudioValidator:
    """Validate filename, media type, size, and basic file signature."""

    ALLOWED_TYPES: Mapping[str, set[str]] = {
        ".mp3": {"audio/mpeg", "audio/mp3"},
        ".wav": {"audio/wav", "audio/x-wav"},
        ".m4a": {"audio/mp4", "audio/x-m4a"},
        ".ogg": {"audio/ogg", "application/ogg"},
        ".webm": {"audio/webm", "video/webm"},
    }

    def __init__(self, max_size: int = settings.MAX_UPLOAD_SIZE) -> None:
        self.max_size = max_size

    @staticmethod
    def normalize_content_type(content_type: str) -> str:
        """Return the base MIME type, ignoring codec parameters added by browsers."""
        return content_type.split(";", 1)[0].strip().lower()

    def validate_metadata(self, filename: str, content_type: str) -> str:
        """Validate filename and declared MIME type before reading the upload."""
        if (
            not filename
            or "\x00" in filename
            or "/" in filename
            or "\\" in filename
            or Path(filename).name != filename
        ):
            raise AudioUploadError("Invalid audio filename")

        extension = Path(filename).suffix.lower()
        allowed_mime_types = self.ALLOWED_TYPES.get(extension)
        if not allowed_mime_types:
            raise AudioFormatError(f"Unsupported audio extension: {extension or 'none'}")
        normalized_content_type = self.normalize_content_type(content_type)
        if normalized_content_type not in allowed_mime_types:
            raise AudioFormatError(
                f"Content type {content_type} does not match extension {extension}"
            )
        return extension

    def validate_staged(
        self,
        filename: str,
        content_type: str,
        size_bytes: int,
        header: bytes,
    ) -> None:
        """Validate size and signature after bounded staging to disk."""
        extension = self.validate_metadata(filename, content_type)
        if size_bytes <= 0:
            raise AudioUploadError("Audio file cannot be empty")
        if size_bytes > self.max_size:
            raise AudioUploadError(
                f"Audio file exceeds the maximum size of {self.max_size} bytes"
            )
        if not self._signature_matches(extension, header):
            raise AudioFormatError("File content does not match the declared audio format")

    def validate(self, filename: str, content_type: str, content: bytes) -> None:
        """Backward-compatible bytes validator used by unit tests and adapters."""
        self.validate_staged(
            filename=filename,
            content_type=content_type,
            size_bytes=len(content),
            header=content[:64],
        )

    @staticmethod
    def _signature_matches(extension: str, content: bytes) -> bool:
        if extension == ".wav":
            return len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WAVE"
        if extension == ".ogg":
            return content.startswith(b"OggS")
        if extension == ".webm":
            return content.startswith(b"\x1a\x45\xdf\xa3")
        if extension == ".m4a":
            return len(content) >= 12 and content[4:8] == b"ftyp"
        if extension == ".mp3":
            return content.startswith(b"ID3") or (
                len(content) >= 2 and content[0] == 0xFF and (content[1] & 0xE0) == 0xE0
            )
        return False
