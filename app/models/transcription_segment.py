"""Timestamped segments produced by speech-to-text."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.transcription import Transcription


class TranscriptionSegment(Base):
    """One ordered timestamped segment of a transcription."""

    __tablename__ = "transcription_segments"
    __table_args__ = (
        UniqueConstraint("transcription_id", "sequence", name="uq_transcription_segment_sequence"),
        Index("ix_transcription_segments_transcription_id", "transcription_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transcription_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("transcriptions.id", ondelete="CASCADE"),
        nullable=False,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    transcription: Mapped["Transcription"] = relationship(
        "Transcription",
        back_populates="segments",
    )
