"""Speaker segment database model."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.database.base import Base


class SpeakerSegment(Base):
    """Timestamped speaker-labelled segment associated with a transcription."""

    __tablename__ = "speaker_segments"

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
