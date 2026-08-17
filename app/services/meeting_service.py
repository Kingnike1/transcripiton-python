"""Business logic and transaction boundaries for meeting operations."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.enums import ProcessingStatus
from app.core.time import utc_now
from app.database.unit_of_work import SqlAlchemyUnitOfWork
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate, MeetingUpdate


class MeetingService:
    """Manage meetings and own transaction boundaries for write use cases."""

    def __init__(self, db: Session) -> None:
        self.uow = SqlAlchemyUnitOfWork(db)
        self.repository = self.uow.meetings

    def create(self, meeting: MeetingCreate, owner_id: int | None = None) -> Meeting:
        if not meeting.title or len(meeting.title.strip()) < 3:
            raise ValueError("Meeting title must be at least 3 characters")

        now = utc_now()
        db_meeting = Meeting(
            owner_id=owner_id,
            title=meeting.title.strip(),
            description=meeting.description,
            status=ProcessingStatus.CREATED.value,
            created_at=now,
            updated_at=now,
        )
        with self.uow.transaction():
            self.repository.create(db_meeting)
        return self.uow.refresh(db_meeting)

    def get_all(self, skip: int = 0, limit: int = 10, owner_id: int | None = None) -> List[Meeting]:
        return self.repository.get_all(skip=skip, limit=limit, owner_id=owner_id)

    def get_by_id(self, meeting_id: int, owner_id: int | None = None) -> Optional[Meeting]:
        if owner_id is None:
            return self.repository.get_by_id(meeting_id)
        return self.repository.get_by_id_for_owner(meeting_id, owner_id)

    def update(self, meeting_id: int, meeting: MeetingUpdate, owner_id: int | None = None) -> Optional[Meeting]:
        with self.uow.transaction():
            db_meeting = self.get_by_id(meeting_id, owner_id=owner_id)
            if not db_meeting:
                return None
            for key, value in meeting.model_dump(exclude_unset=True).items():
                setattr(db_meeting, key, value)
            db_meeting.updated_at = utc_now()
            self.repository.update(db_meeting)
        return self.uow.refresh(db_meeting)

    def delete(self, meeting_id: int, owner_id: int | None = None) -> bool:
        with self.uow.transaction():
            if owner_id is not None:
                db_meeting = self.repository.get_by_id_for_owner(meeting_id, owner_id)
                if db_meeting is None:
                    return False
                db_meeting.soft_delete()
                self.repository.update(db_meeting)
                return True
            return self.repository.delete(meeting_id)

    def count(self, owner_id: int | None = None) -> int:
        return self.repository.count(owner_id=owner_id)

    def search(self, query: str, skip: int = 0, limit: int = 10, owner_id: int | None = None) -> List[Meeting]:
        return self.repository.search(query, skip=skip, limit=limit, owner_id=owner_id)

    def count_search(self, query: str, owner_id: int | None = None) -> int:
        return self.repository.count_search(query, owner_id=owner_id)

    def transition_status(self, meeting_id: int, new_status: ProcessingStatus) -> bool:
        with self.uow.transaction():
            db_meeting = self.repository.get_by_id(meeting_id)
            if not db_meeting or not db_meeting.transition_status(new_status):
                return False
            self.repository.update(db_meeting)
            return True

    def get_by_status(self, status: ProcessingStatus) -> List[Meeting]:
        return self.repository.get_by_status(status.value)
