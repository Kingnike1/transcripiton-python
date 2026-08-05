"""Dependency injection module for AMIP."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.audio_service import AudioService
from app.services.meeting_service import MeetingService


def get_meeting_service(db: Session = Depends(get_db)) -> MeetingService:
    return MeetingService(db)


def get_audio_service(db: Session = Depends(get_db)) -> AudioService:
    return AudioService(db)
