"""Explicit SQLAlchemy unit-of-work coordination.

The service layer owns transaction boundaries. Repositories stage changes and
flush them, while this unit of work commits or rolls back the shared session.
"""

from contextlib import contextmanager
from typing import Iterator, TypeVar

from sqlalchemy.orm import Session

from app.database.audio_repository import AudioRepository
from app.database.meeting_repository import MeetingRepository

T = TypeVar("T")


class SqlAlchemyUnitOfWork:
    """Coordinate repositories that participate in one SQLAlchemy transaction."""

    def __init__(self, session: Session) -> None:
        """Create a unit of work around an existing SQLAlchemy session."""
        self.session = session
        self.meetings = MeetingRepository(session)
        self.audios = AudioRepository(session)

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Commit staged changes on success and roll them back on failure."""
        try:
            yield
            self.commit()
        except Exception:
            self.rollback()
            raise

    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()

    def refresh(self, entity: T) -> T:
        """Refresh a persisted entity and return it for convenient chaining."""
        self.session.refresh(entity)
        return entity
