"""Application service for secure meeting audio uploads."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.core.enums import ProcessingStatus
from app.database.audio_repository import AudioRepository
from app.database.meeting_repository import MeetingRepository
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
        self.db = db
        self.meetings = MeetingRepository(db)
        self.audios = AudioRepository(db)
        self.storage = storage or StorageService()
        self.validator = validator or AudioValidator()

    def upload(
        self,
        meeting_id: int,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> Audio:
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
            self.audios.add(audio)
            meeting.status = ProcessingStatus.AUDIO_UPLOADED.value
            meeting.updated_at = now
            self.db.commit()
            self.db.refresh(audio)
            return audio
        except Exception:
            self.db.rollback()
            if stored_path:
                self.storage.delete_file(stored_path)
            raise

    def get_for_meeting(self, meeting_id: int) -> Optional[Audio]:
        if self.meetings.get_by_id(meeting_id) is None:
            raise MeetingNotFoundError(f"Meeting {meeting_id} was not found")
        return self.audios.get_by_meeting_id(meeting_id)
