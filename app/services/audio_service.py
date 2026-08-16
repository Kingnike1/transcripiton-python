"""Application service for secure meeting audio uploads."""

from datetime import datetime, timezone
from io import BytesIO
import math
from pathlib import Path
from typing import BinaryIO, Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.core.enums import ProcessingStatus
from app.database.unit_of_work import SqlAlchemyUnitOfWork
from app.exceptions.audio import (
    AudioAlreadyExistsError,
    AudioUploadError,
    MeetingNotFoundError,
)
from app.models.audio import Audio
from app.services.audio_inspector import AudioInspector, FFprobeAudioInspector
from app.services.audio_upload_stager import (
    AudioSizeLimitExceeded,
    AudioUploadStager,
    StagedAudioUpload,
)
from app.services.audio_validator import AudioValidator
from app.services.storage_service import StorageService


class AudioService:
    """Coordinate staged upload, validation, storage, and persistence."""

    def __init__(
        self,
        db: Session,
        storage: Optional[StorageService] = None,
        validator: Optional[AudioValidator] = None,
        inspector: Optional[AudioInspector] = None,
        stager: Optional[AudioUploadStager] = None,
    ) -> None:
        self.uow = SqlAlchemyUnitOfWork(db)
        self.meetings = self.uow.meetings
        self.audios = self.uow.audios
        self.storage = storage or StorageService()
        self.validator = validator or AudioValidator()
        self.inspector: AudioInspector = inspector or FFprobeAudioInspector(
            binary=settings.audio.FFPROBE_BINARY,
            timeout_seconds=settings.audio.FFPROBE_TIMEOUT_SECONDS,
        )
        self.stager = stager or AudioUploadStager(self.storage)

    def upload(
        self,
        meeting_id: int,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> Audio:
        """Backward-compatible adapter that routes bytes through streaming logic."""
        return self.upload_stream(
            meeting_id=meeting_id,
            filename=filename,
            content_type=content_type,
            stream=BytesIO(content),
        )

    def upload_stream(
        self,
        meeting_id: int,
        filename: str,
        content_type: str,
        stream: BinaryIO,
    ) -> Audio:
        """Stage an upload in chunks, validate it, then persist it atomically."""
        meeting = self.meetings.get_by_id(meeting_id)
        if meeting is None:
            raise MeetingNotFoundError(f"Meeting {meeting_id} was not found")
        if self.audios.get_by_meeting_id(meeting_id) is not None:
            raise AudioAlreadyExistsError("This meeting already has an uploaded audio file")

        self.validator.validate_metadata(filename, content_type)
        if not ProcessingStatus(meeting.status).can_transition_to(
            ProcessingStatus.AUDIO_UPLOADED
        ):
            raise AudioUploadError(
                f"Audio cannot be uploaded while meeting is in status {meeting.status}"
            )

        staged: Optional[StagedAudioUpload] = None
        stored_path: Optional[str] = None
        database_committed = False

        try:
            try:
                staged = self.stager.stage(
                    stream,
                    max_size=self.validator.max_size,
                    original_name=filename,
                )
            except AudioSizeLimitExceeded as exc:
                raise AudioUploadError(
                    f"Audio file exceeds the maximum size of {self.validator.max_size} bytes"
                ) from exc

            header = self.stager.read_prefix(staged)
            self.validator.validate_staged(
                filename=filename,
                content_type=content_type,
                size_bytes=staged.size_bytes,
                header=header,
            )
            media = self.inspector.inspect(staged.absolute_path)

            stored_path = self.stager.promote(
                staged=staged,
                original_name=filename,
                meeting_id=meeting_id,
            )
            size_bytes = staged.size_bytes
            staged = None

            now = datetime.now(timezone.utc)
            duration = (
                max(0, math.ceil(media.duration_seconds))
                if media.duration_seconds is not None
                else None
            )
            audio = Audio(
                meeting_id=meeting_id,
                filename=Path(filename).name,
                file_path=stored_path,
                file_size=size_bytes,
                mime_type=content_type.lower(),
                duration=duration,
                codec_name=media.codec_name,
                channels=media.channels,
                sample_rate=media.sample_rate,
                created_at=now,
                updated_at=now,
            )

            with self.uow.transaction():
                self.audios.add(audio)
                if not meeting.transition_status(ProcessingStatus.AUDIO_UPLOADED):
                    raise AudioUploadError(
                        f"Audio cannot be uploaded while meeting is in status {meeting.status}"
                    )
                self.meetings.update(meeting)

            database_committed = True
            return self.uow.refresh(audio)
        except Exception:
            if staged is not None:
                self.stager.discard(staged)
            if stored_path and not database_committed:
                self.storage.delete_file(stored_path)
            raise

    def get_for_meeting(self, meeting_id: int) -> Optional[Audio]:
        """Return audio metadata for an existing meeting."""
        if self.meetings.get_by_id(meeting_id) is None:
            raise MeetingNotFoundError(f"Meeting {meeting_id} was not found")
        return self.audios.get_by_meeting_id(meeting_id)
