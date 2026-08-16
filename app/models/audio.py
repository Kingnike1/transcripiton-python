"""Audio database model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.database.base import Base


class Audio(Base):
    """Stored meeting audio with at most one active row per meeting."""

    __tablename__ = "audios"
    __table_args__ = (
        Index(
            "uq_audios_active_meeting",
            "meeting_id",
            unique=True,
            sqlite_where=text("deleted_at IS NULL"),
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("meetings.id"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    codec_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    channels: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sample_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="audios")
    transcription = relationship("Transcription", back_populates="audio", uselist=False)
