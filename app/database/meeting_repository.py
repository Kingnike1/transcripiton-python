"""
Meeting repository implementation.
Concrete repository for Meeting model data access.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.repository import BaseRepository
from app.models.meeting import Meeting


class MeetingRepository(BaseRepository[Meeting]):
    """Repository for Meeting model.

    Repositories stage persistence changes only. Transaction boundaries belong
    to the service layer through the application's unit of work.
    """

    def __init__(self, db: Session):
        """Initialize meeting repository.

        Args:
            db: Database session
        """
        self.db = db

    def get_by_id(self, id: int) -> Optional[Meeting]:
        """Get meeting by ID (excluding soft-deleted).

        Args:
            id: Meeting ID

        Returns:
            Meeting instance if found and not deleted, None otherwise
        """
        return (
            self.db.query(Meeting)
            .filter(Meeting.id == id)
            .filter(Meeting.deleted_at.is_(None))
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 10) -> List[Meeting]:
        """Get all active meetings with pagination.

        Args:
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            List of active Meeting instances, ordered by creation date descending
        """
        return (
            self.db.query(Meeting)
            .filter(Meeting.deleted_at.is_(None))
            .order_by(Meeting.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, entity: Meeting) -> Meeting:
        """Stage a new meeting without committing the transaction."""
        self.db.add(entity)
        self.db.flush()
        return entity

    def update(self, entity: Meeting) -> Meeting:
        """Stage meeting changes without committing the transaction."""
        self.db.add(entity)
        self.db.flush()
        return entity

    def delete(self, id: int) -> bool:
        """Stage a meeting soft delete without committing the transaction.

        Args:
            id: Meeting ID to delete

        Returns:
            True if staged for deletion, False if not found
        """
        meeting = self.get_by_id(id)
        if not meeting:
            return False

        meeting.soft_delete()
        self.db.flush()
        return True

    def count(self) -> int:
        """Count total active meetings.

        Returns:
            Number of non-deleted meetings
        """
        return self.db.query(Meeting).filter(Meeting.deleted_at.is_(None)).count()

    def search(self, query: str, skip: int = 0, limit: int = 10) -> List[Meeting]:
        """Search meetings by title or description.

        Args:
            query: Search term
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            List of matching Meeting instances
        """
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
        """Count meetings matching search query.

        Args:
            query: Search term

        Returns:
            Number of matching meetings
        """
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
        """Get meetings by processing status.

        Args:
            status: Processing status value

        Returns:
            List of Meeting instances with given status
        """
        return (
            self.db.query(Meeting)
            .filter(Meeting.status == status)
            .filter(Meeting.deleted_at.is_(None))
            .order_by(Meeting.created_at.desc())
            .all()
        )

    def get_stale_processing(self, minutes: int = 30) -> List[Meeting]:
        """Get meetings stuck in processing for too long.

        Args:
            minutes: Threshold in minutes

        Returns:
            List of Meeting instances stuck in processing
        """
        cutoff = datetime.utcnow()

        return (
            self.db.query(Meeting)
            .filter(Meeting.deleted_at.is_(None))
            .filter(
                Meeting.status.in_(["TRANSCRIBING", "DIARIZING", "SUMMARIZING"])
            )
            .filter(Meeting.updated_at < cutoff)
            .all()
        )
