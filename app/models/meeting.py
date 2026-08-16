"""Meeting database model."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ProcessingStatus
from app.core.time import utc_now
from app.database.base import Base


class Meeting(Base):
    """Meeting aggregate root with processing status and soft deletion."""

    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default=ProcessingStatus.CREATED.value, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    audios: Mapped[List["Audio"]] = relationship("Audio", back_populates="meeting")
    analysis: Mapped[Optional["MeetingAnalysis"]] = relationship(
        "MeetingAnalysis", back_populates="meeting", uselist=False
    )

    def is_active(self) -> bool:
        """Return whether the meeting has not been soft-deleted."""
        return self.deleted_at is None

    def soft_delete(self) -> None:
        """Soft-delete the meeting using the shared UTC clock."""
        now = utc_now()
        self.deleted_at = now
        self.updated_at = now

    def __repr__(self) -> str:
        """Return a compact debugging representation."""
        return f"<Meeting(id={self.id}, title='{self.title}', status='{self.status}')>"

    def transition_status(self, new_status: ProcessingStatus) -> bool:
        """Apply a valid processing-status transition."""
        current = ProcessingStatus(self.status)
        if not current.can_transition_to(new_status):
            return False

        self.status = new_status.value
        self.updated_at = utc_now()
        return True
