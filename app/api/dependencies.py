"""Dependency injection module for AMIP."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.audio_service import AudioService
from app.services.meeting_service import MeetingService
from app.services.persistent_job_service import PersistentJobService
from app.services.transcription_service import TranscriptionService


def get_meeting_service(db: Session = Depends(get_db)) -> MeetingService:
    return MeetingService(db)


def get_audio_service(db: Session = Depends(get_db)) -> AudioService:
    return AudioService(db)


def get_job_service(db: Session = Depends(get_db)) -> PersistentJobService:
    return PersistentJobService(db)


def get_transcription_service(db: Session = Depends(get_db)) -> TranscriptionService:
    return TranscriptionService(db)
