"""
MeetingAnalysis database model.
"""

from datetime import datetime
from sqlalchemy import Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MeetingAnalysis(Base):
    __tablename__ = "meeting_analysis"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(Integer, ForeignKey("meetings.id"), unique=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    action_items: Mapped[str] = mapped_column(Text, nullable=True)
    decisions: Mapped[str] = mapped_column(Text, nullable=True)
    risks: Mapped[str] = mapped_column(Text, nullable=True)
    open_questions: Mapped[str] = mapped_column(Text, nullable=True)
    follow_up_tasks: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="analysis")
