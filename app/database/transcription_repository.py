"""Persistence operations for transcriptions and timestamped segments."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.transcription import Transcription


class TranscriptionRepository:
    """Transaction-neutral repository for transcription aggregates."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, transcription_id: int) -> Optional[Transcription]:
        stmt = (
            select(Transcription)
            .options(selectinload(Transcription.segments))
            .where(
                Transcription.id == transcription_id,
                Transcription.deleted_at.is_(None),
            )
        )
        return self.session.scalar(stmt)

    def get_by_audio_id(self, audio_id: int) -> Optional[Transcription]:
        stmt = (
            select(Transcription)
            .options(selectinload(Transcription.segments))
            .where(
                Transcription.audio_id == audio_id,
                Transcription.deleted_at.is_(None),
            )
        )
        return self.session.scalar(stmt)

    def get_by_meeting_id(self, meeting_id: int) -> Optional[Transcription]:
        from app.models.audio import Audio

        stmt = (
            select(Transcription)
            .join(Audio, Transcription.audio_id == Audio.id)
            .options(selectinload(Transcription.segments))
            .where(
                Audio.meeting_id == meeting_id,
                Audio.deleted_at.is_(None),
                Transcription.deleted_at.is_(None),
            )
            .order_by(Transcription.created_at.desc())
            .limit(1)
        )
        return self.session.scalar(stmt)

    def add(self, transcription: Transcription) -> Transcription:
        self.session.add(transcription)
        self.session.flush()
        return transcription
