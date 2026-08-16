"""Application service for persisted speech-to-text results."""

from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import ProcessingStatus
from app.database.unit_of_work import SqlAlchemyUnitOfWork
from app.models.transcription import Transcription
from app.models.transcription_segment import TranscriptionSegment
from app.services.interfaces import TranscriptResult


class TranscriptionService:
    """Persist and query the transcription aggregate."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.uow = SqlAlchemyUnitOfWork(session)

    def get_by_meeting(self, meeting_id: int) -> Optional[Transcription]:
        return self.uow.transcriptions.get_by_meeting_id(meeting_id)

    def persist_result(
        self,
        meeting_id: int,
        audio_id: int,
        result: TranscriptResult,
    ) -> Transcription:
        """Persist result once and move the meeting to TRANSCRIBED atomically."""
        existing = self.uow.transcriptions.get_by_audio_id(audio_id)
        if existing is not None:
            return existing

        meeting = self.uow.meetings.get_by_id(meeting_id)
        if meeting is None:
            raise ValueError("Meeting not found")
        if meeting.status != ProcessingStatus.TRANSCRIBING.value:
            raise ValueError(f"Meeting is not transcribing: {meeting.status}")

        transcription = Transcription(
            audio_id=audio_id,
            text=result.text,
            language=result.language,
            segments=[
                TranscriptionSegment(
                    sequence=index,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    text=segment.text,
                    confidence=segment.confidence,
                )
                for index, segment in enumerate(result.segments or [], start=1)
            ],
        )
        if not meeting.transition_status(ProcessingStatus.TRANSCRIBED):
            raise ValueError("Invalid transition to TRANSCRIBED")

        try:
            with self.uow.transaction():
                self.uow.transcriptions.add(transcription)
                self.session.flush()
        except IntegrityError:
            self.session.rollback()
            existing = self.uow.transcriptions.get_by_audio_id(audio_id)
            if existing is not None:
                return existing
            raise

        return self.uow.transcriptions.get_by_id(transcription.id) or transcription
