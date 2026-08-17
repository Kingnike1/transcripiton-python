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
        self.db = db

    def get_by_id(self, id: int) -> Optional[Meeting]:
        return self.db.query(Meeting).filter(Meeting.id == id, Meeting.deleted_at.is_(None)).first()

    def get_by_id_for_owner(self, id: int, owner_id: int) -> Optional[Meeting]:
        return (
            self.db.query(Meeting)
            .filter(Meeting.id == id, Meeting.owner_id == owner_id, Meeting.deleted_at.is_(None))
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 10, owner_id: int | None = None) -> List[Meeting]:
        query = self.db.query(Meeting).filter(Meeting.deleted_at.is_(None))
        if owner_id is not None:
            query = query.filter(Meeting.owner_id == owner_id)
        return query.order_by(Meeting.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, entity: Meeting) -> Meeting:
        self.db.add(entity)
        self.db.flush()
        return entity

    def update(self, entity: Meeting) -> Meeting:
        self.db.add(entity)
        self.db.flush()
        return entity

    def delete(self, id: int) -> bool:
        meeting = self.get_by_id(id)
        if not meeting:
            return False
        meeting.soft_delete()
        self.db.flush()
        return True

    def count(self, owner_id: int | None = None) -> int:
        query = self.db.query(Meeting).filter(Meeting.deleted_at.is_(None))
        if owner_id is not None:
            query = query.filter(Meeting.owner_id == owner_id)
        return query.count()

    def search(self, query: str, skip: int = 0, limit: int = 10, owner_id: int | None = None) -> List[Meeting]:
        search_pattern = f"%{query}%"
        db_query = self.db.query(Meeting).filter(Meeting.deleted_at.is_(None))
        if owner_id is not None:
            db_query = db_query.filter(Meeting.owner_id == owner_id)
        return (
            db_query.filter((Meeting.title.ilike(search_pattern)) | (Meeting.description.ilike(search_pattern)))
            .order_by(Meeting.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_search(self, query: str, owner_id: int | None = None) -> int:
        search_pattern = f"%{query}%"
        db_query = self.db.query(Meeting).filter(Meeting.deleted_at.is_(None))
        if owner_id is not None:
            db_query = db_query.filter(Meeting.owner_id == owner_id)
        return db_query.filter(
            (Meeting.title.ilike(search_pattern)) | (Meeting.description.ilike(search_pattern))
        ).count()

    def get_by_status(self, status: str) -> List[Meeting]:
        return (
            self.db.query(Meeting)
            .filter(Meeting.status == status, Meeting.deleted_at.is_(None))
            .order_by(Meeting.created_at.desc())
            .all()
        )

    def get_stale_processing(self, minutes: int = 30) -> List[Meeting]:
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
