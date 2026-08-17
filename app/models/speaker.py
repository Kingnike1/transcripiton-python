"""Speaker segment database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.transcription import Transcription


class SpeakerSegment(Base):
    """Timestamped speaker-labelled segment associated with a transcription."""

    __tablename__ = "speaker_segments"
    __table_args__ = (
        Index("ix_speaker_segments_transcription_start", "transcription_id", "start_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transcription_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("transcriptions.id"),
        nullable=False,
    )
    speaker_label: Mapped[str] = mapped_column(String(50), nullable=True)
    start_time: Mapped[float] = mapped_column(Float)
    end_time: Mapped[float] = mapped_column(Float)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    transcription: Mapped["Transcription"] = relationship(
        "Transcription",
        back_populates="speaker_segments",
    )
