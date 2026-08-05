"""Persistence operations for meeting audio records."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.audio import Audio


class AudioRepository:
    """Repository dedicated to audio metadata persistence."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, audio_id: int) -> Optional[Audio]:
        return (
            self.db.query(Audio)
            .filter(Audio.id == audio_id, Audio.deleted_at.is_(None))
            .first()
        )

    def get_by_meeting_id(self, meeting_id: int) -> Optional[Audio]:
        return (
            self.db.query(Audio)
            .filter(Audio.meeting_id == meeting_id, Audio.deleted_at.is_(None))
            .order_by(Audio.created_at.desc())
            .first()
        )

    def add(self, audio: Audio) -> Audio:
        """Stage an audio record without committing the transaction."""
        self.db.add(audio)
        self.db.flush()
        return audio
