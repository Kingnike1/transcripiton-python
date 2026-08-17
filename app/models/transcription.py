"""Transcription database model."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.audio import Audio
    from app.models.speaker import SpeakerSegment
    from app.models.transcription_segment import TranscriptionSegment


class Transcription(Base):
    """Persisted speech-to-text result for one audio resource."""

    __tablename__ = "transcriptions"
    __table_args__ = (Index("uq_transcriptions_audio_id", "audio_id", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    audio_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("audios.id"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    audio: Mapped["Audio"] = relationship("Audio", back_populates="transcription")
    segments: Mapped[List["TranscriptionSegment"]] = relationship(
        "TranscriptionSegment",
        back_populates="transcription",
        cascade="all, delete-orphan",
        order_by="TranscriptionSegment.sequence",
    )
    speaker_segments: Mapped[List["SpeakerSegment"]] = relationship(
        "SpeakerSegment",
        back_populates="transcription",
    )
