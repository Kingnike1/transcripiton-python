"""
Transcription database model.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    audio_id: Mapped[int] = mapped_column(Integer, ForeignKey("audios.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    audio: Mapped["Audio"] = relationship("Audio", back_populates="transcription")
    speaker_segments = relationship("SpeakerSegment", back_populates="transcription")
