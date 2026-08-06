"""
Meeting service module.
Contains business logic and transaction boundaries for meeting operations.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.enums import ProcessingStatus
from app.database.unit_of_work import SqlAlchemyUnitOfWork
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate, MeetingUpdate


class MeetingService:
    """Manage meetings and own transaction boundaries for write use cases."""

    def __init__(self, db: Session):
        """Initialize the service with one request-scoped database session."""
        self.uow = SqlAlchemyUnitOfWork(db)
        # Kept as a compatibility alias for existing callers and tests.
        self.repository = self.uow.meetings

    def create(self, meeting: MeetingCreate) -> Meeting:
        """Create and commit a new meeting."""
        if not meeting.title or len(meeting.title.strip()) < 3:
            raise ValueError("Meeting title must be at least 3 characters")

        db_meeting = Meeting(
            title=meeting.title.strip(),
            description=meeting.description,
            status=ProcessingStatus.CREATED.value,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        with self.uow.transaction():
            self.repository.create(db_meeting)

        return self.uow.refresh(db_meeting)

    def get_all(self, skip: int = 0, limit: int = 10) -> List[Meeting]:
        """Get all active meetings with pagination."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_by_id(self, meeting_id: int) -> Optional[Meeting]:
        """Get an active meeting by ID."""
        return self.repository.get_by_id(meeting_id)

    def update(self, meeting_id: int, meeting: MeetingUpdate) -> Optional[Meeting]:
        """Update and commit an existing meeting."""
        with self.uow.transaction():
            db_meeting = self.repository.get_by_id(meeting_id)
            if not db_meeting:
                return None

            update_data = meeting.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_meeting, key, value)

            db_meeting.updated_at = datetime.now(timezone.utc)
            self.repository.update(db_meeting)

        return self.uow.refresh(db_meeting)

    def delete(self, meeting_id: int) -> bool:
        """Soft delete and commit a meeting."""
        with self.uow.transaction():
            return self.repository.delete(meeting_id)

    def count(self) -> int:
        """Count total active meetings."""
        return self.repository.count()

    def search(self, query: str, skip: int = 0, limit: int = 10) -> List[Meeting]:
        """Search meetings by title or description."""
        return self.repository.search(query, skip=skip, limit=limit)

    def count_search(self, query: str) -> int:
        """Count meetings matching a search query."""
        return self.repository.count_search(query)

    def transition_status(
        self, meeting_id: int, new_status: ProcessingStatus
    ) -> bool:
        """Validate, persist, and commit a meeting status transition."""
        with self.uow.transaction():
            db_meeting = self.repository.get_by_id(meeting_id)
            if not db_meeting:
                return False

            if not db_meeting.transition_status(new_status):
                return False

            self.repository.update(db_meeting)
            return True

    def get_by_status(self, status: ProcessingStatus) -> List[Meeting]:
        """Get active meetings by processing status."""
        return self.repository.get_by_status(status.value)
