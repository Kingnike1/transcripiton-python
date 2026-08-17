"""Explicit SQLAlchemy unit-of-work coordination."""

from contextlib import contextmanager
from typing import Iterator, TypeVar

from sqlalchemy.orm import Session

from app.database.audio_repository import AudioRepository
from app.database.meeting_repository import MeetingRepository
from app.database.processing_job_repository import ProcessingJobRepository
from app.database.transcription_repository import TranscriptionRepository

T = TypeVar("T")


class SqlAlchemyUnitOfWork:
    """Coordinate repositories that participate in one SQLAlchemy transaction."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.meetings = MeetingRepository(session)
        self.audios = AudioRepository(session)
        self.processing_jobs = ProcessingJobRepository(session)
        self.transcriptions = TranscriptionRepository(session)

    @contextmanager
    def transaction(self) -> Iterator[None]:
        try:
            yield
            self.commit()
        except Exception:
            self.rollback()
            raise

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, entity: T) -> T:
        self.session.refresh(entity)
        return entity
