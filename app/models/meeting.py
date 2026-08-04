"""
Meeting database model.
Represents a meeting in the database.
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.core.enums import ProcessingStatus


class Meeting(Base):
    """Meeting model.
    
    Represents a meeting event with title, description, and timestamps.
    Supports soft deletion to preserve data integrity.
    
    Attributes:
        id: Unique identifier
        title: Meeting title
        description: Meeting description
        created_at: Creation timestamp
        updated_at: Last update timestamp
        deleted_at: Soft delete timestamp
    """
    
    __tablename__ = "meetings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default=ProcessingStatus.CREATED.value, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    audios: Mapped[List["Audio"]] = relationship("Audio", back_populates="meeting")
    analysis: Mapped[Optional["MeetingAnalysis"]] = relationship(
        "MeetingAnalysis", back_populates="meeting", uselist=False
    )
    
    def is_active(self) -> bool:
        """Check if meeting is not soft-deleted.
        
        Returns:
            True if meeting is active, False if soft-deleted
        """
        return self.deleted_at is None
    
    def soft_delete(self) -> None:
        """Soft delete the meeting by setting deleted_at timestamp."""
        self.deleted_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def __repr__(self) -> str:
        """String representation of meeting.
        
        Returns:
            String with meeting ID and title
        """
        return f"<Meeting(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    def transition_status(self, new_status: ProcessingStatus) -> bool:
        """Transition meeting to a new processing status.
        
        Validates the transition before applying it.
        
        Args:
            new_status: Target processing status
            
        Returns:
            True if transition was applied, False if invalid
        """
        current = ProcessingStatus(self.status)
        
        if not current.can_transition_to(new_status):
            return False
        
        self.status = new_status.value
        self.updated_at = datetime.now(timezone.utc)
        return True
