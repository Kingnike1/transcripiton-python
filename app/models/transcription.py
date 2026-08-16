"""Transcription database model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.database.base import Base


class Transcription(Base):
    """Persisted transcription produced from one audio resource."""

    __tablename__ = "transcriptions"

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
    speaker_segments = relationship(
        "SpeakerSegment",
        back_populates="transcription",
    )
