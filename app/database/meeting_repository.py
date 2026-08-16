"""Meeting repository implementation."""

from datetime import timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.enums import ProcessingStatus
from app.core.time import utc_now
from app.database.repository import BaseRepository
from app.models.meeting import Meeting


class MeetingRepository(BaseRepository[Meeting]):
    """Persist meetings without owning transaction boundaries."""

    def __init__(self, db: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.db = db

    def get_by_id(self, id: int) -> Optional[Meeting]:
        """Return an active meeting by ID."""
        return (
            self.db.query(Meeting)
            .filter(Meeting.id == id)
            .filter(Meeting.deleted_at.is_(None))
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 10) -> List[Meeting]:
        """Return active meetings ordered newest first."""
        return (
            self.db.query(Meeting)
            .filter(Meeting.deleted_at.is_(None))
            .order_by(Meeting.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, entity: Meeting) -> Meeting:
        """Stage a new meeting without committing."""
        self.db.add(entity)
        self.db.flush()
        return entity

    def update(self, entity: Meeting) -> Meeting:
        """Stage meeting changes without committing."""
        self.db.add(entity)
        self.db.flush()
        return entity

    def delete(self, id: int) -> bool:
        """Stage a soft delete for an active meeting."""
        meeting = self.get_by_id(id)
        if not meeting:
            return False

        meeting.soft_delete()
        self.db.flush()
        return True

    def count(self) -> int:
        """Count active meetings."""
        return self.db.query(Meeting).filter(Meeting.deleted_at.is_(None)).count()

    def search(self, query: str, skip: int = 0, limit: int = 10) -> List[Meeting]:
        """Search active meetings by title or description."""
        search_pattern = f"%{query}%"
        return (
            self.db.query(Meeting)
            .filter(Meeting.deleted_at.is_(None))
            .filter(
                (Meeting.title.ilike(search_pattern))
                | (Meeting.description.ilike(search_pattern))
            )
            .order_by(Meeting.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_search(self, query: str) -> int:
        """Count active meetings matching a search query."""
        search_pattern = f"%{query}%"
        return (
            self.db.query(Meeting)
            .filter(Meeting.deleted_at.is_(None))
            .filter(
                (Meeting.title.ilike(search_pattern))
                | (Meeting.description.ilike(search_pattern))
            )
            .count()
        )

    def get_by_status(self, status: str) -> List[Meeting]:
        """Return active meetings with the supplied processing status."""
        return (
            self.db.query(Meeting)
            .filter(Meeting.status == status)
            .filter(Meeting.deleted_at.is_(None))
            .order_by(Meeting.created_at.desc())
            .all()
        )

    def get_stale_processing(self, minutes: int = 30) -> List[Meeting]:
        """Return processing meetings not updated within the requested threshold."""
        if minutes <= 0:
            raise ValueError("minutes must be greater than zero")

        cutoff = utc_now() - timedelta(minutes=minutes)
        processing_statuses = [
            ProcessingStatus.TRANSCRIBING.value,
            ProcessingStatus.DIARIZING.value,
            ProcessingStatus.SUMMARIZING.value,
        ]
        return (
            self.db.query(Meeting)
            .filter(Meeting.deleted_at.is_(None))
            .filter(Meeting.status.in_(processing_statuses))
            .filter(Meeting.updated_at < cutoff)
            .all()
        )
