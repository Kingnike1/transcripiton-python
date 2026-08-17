"""Participant identity model for mapping diarization labels to people."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.meeting import Meeting


class Participant(Base):
    """Human identity assigned to a diarization speaker label within one meeting."""

    __tablename__ = "participants"
    __table_args__ = (
        UniqueConstraint(
            "meeting_id",
            "speaker_label",
            name="uq_participants_meeting_speaker_label",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    speaker_label: Mapped[str] = mapped_column(String(50), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="participants")
