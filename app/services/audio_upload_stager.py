"""Chunked staging and atomic promotion for uploaded audio files."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from app.services.storage_service import StorageService


class AudioSizeLimitExceeded(Exception):
    """Internal signal raised as soon as a streamed upload exceeds its limit."""


@dataclass(frozen=True)
class StagedAudioUpload:
    """Reference to a temporary upload written under the storage root."""

    relative_path: str
    absolute_path: Path
    size_bytes: int


class AudioUploadStager:
    """Write uploads incrementally and promote validated files atomically."""

    DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1 MiB

    def __init__(self, storage: StorageService, chunk_size: int = DEFAULT_CHUNK_SIZE) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        self.storage = storage
        self.chunk_size = chunk_size

    def stage(self, stream: BinaryIO, max_size: int) -> StagedAudioUpload:
        """Copy a binary stream to temporary storage while enforcing max size."""
        temp_dir = self.storage.get_path(StorageService.TEMP_DIR)
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / f"{uuid4()}.upload"
        total = 0

        try:
            try:
                stream.seek(0)
            except (AttributeError, OSError):
                pass

            with temp_path.open("wb") as destination:
                while True:
                    chunk = stream.read(self.chunk_size)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_size:
                        raise AudioSizeLimitExceeded
                    destination.write(chunk)

            relative_path = str(temp_path.relative_to(self.storage.base_path))
            return StagedAudioUpload(
                relative_path=relative_path,
                absolute_path=temp_path,
                size_bytes=total,
            )
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    def read_prefix(self, staged: StagedAudioUpload, size: int = 64) -> bytes:
        """Read only the bytes required for lightweight signature validation."""
        with staged.absolute_path.open("rb") as source:
            return source.read(size)

    def promote(
        self,
        staged: StagedAudioUpload,
        original_name: str,
        meeting_id: int,
    ) -> str:
        """Atomically move a validated staged upload into its final audio path."""
        meeting_dir = self.storage.get_path(StorageService.AUDIO_DIR) / str(meeting_id)
        meeting_dir.mkdir(parents=True, exist_ok=True)

        extension = Path(original_name).suffix.lower()
        final_path = meeting_dir / f"{uuid4()}{extension}"
        os.replace(staged.absolute_path, final_path)
        return str(final_path.relative_to(self.storage.base_path))

    def discard(self, staged: StagedAudioUpload) -> None:
        """Delete a staged file if it still exists."""
        staged.absolute_path.unlink(missing_ok=True)
