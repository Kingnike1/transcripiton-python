"""Meeting analysis database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.database.base import Base


class MeetingAnalysis(Base):
    """Structured analysis payload associated one-to-one with a meeting."""

    __tablename__ = "meeting_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("meetings.id"),
        unique=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    action_items: Mapped[str] = mapped_column(Text, nullable=True)
    decisions: Mapped[str] = mapped_column(Text, nullable=True)
    risks: Mapped[str] = mapped_column(Text, nullable=True)
    open_questions: Mapped[str] = mapped_column(Text, nullable=True)
    follow_up_tasks: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="analysis")
