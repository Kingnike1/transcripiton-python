"""Application service for secure meeting audio uploads."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.core.enums import ProcessingStatus
from app.database.unit_of_work import SqlAlchemyUnitOfWork
from app.exceptions.audio import (
    AudioAlreadyExistsError,
    AudioUploadError,
    MeetingNotFoundError,
)
from app.models.audio import Audio
from app.services.audio_validator import AudioValidator
from app.services.storage_service import StorageService


class AudioService:
    """Coordinate validation, storage, persistence, and status changes."""

    def __init__(
        self,
        db: Session,
        storage: Optional[StorageService] = None,
        validator: Optional[AudioValidator] = None,
    ) -> None:
        self.uow = SqlAlchemyUnitOfWork(db)
        self.meetings = self.uow.meetings
        self.audios = self.uow.audios
        self.storage = storage or StorageService()
        self.validator = validator or AudioValidator()

    def upload(
        self,
        meeting_id: int,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> Audio:
        """Validate, store, and atomically persist meeting audio metadata."""
        meeting = self.meetings.get_by_id(meeting_id)
        if meeting is None:
            raise MeetingNotFoundError(f"Meeting {meeting_id} was not found")
        if self.audios.get_by_meeting_id(meeting_id) is not None:
            raise AudioAlreadyExistsError("This meeting already has an uploaded audio file")

        self.validator.validate(filename, content_type, content)
        if not ProcessingStatus(meeting.status).can_transition_to(
            ProcessingStatus.AUDIO_UPLOADED
        ):
            raise AudioUploadError(
                f"Audio cannot be uploaded while meeting is in status {meeting.status}"
            )

        stored_path: Optional[str] = None
        database_committed = False
        try:
            stored_path = self.storage.store_audio(content, filename, meeting_id)
            now = datetime.now(timezone.utc)
            audio = Audio(
                meeting_id=meeting_id,
                filename=Path(filename).name,
                file_path=stored_path,
                file_size=len(content),
                mime_type=content_type.lower(),
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
            # Compensate the filesystem only when the database transaction did
            # not commit. A post-commit refresh failure cannot be rolled back.
            if stored_path and not database_committed:
                self.storage.delete_file(stored_path)
            raise

    def get_for_meeting(self, meeting_id: int) -> Optional[Audio]:
        """Return audio metadata for an existing meeting."""
        if self.meetings.get_by_id(meeting_id) is None:
            raise MeetingNotFoundError(f"Meeting {meeting_id} was not found")
        return self.audios.get_by_meeting_id(meeting_id)
