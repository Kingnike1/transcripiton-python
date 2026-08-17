"""Dependency injection and authorization helpers for AMIP."""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.meeting import Meeting
from app.models.processing_job import ProcessingJob
from app.models.user import User
from app.services.auth_service import AuthService, SESSION_COOKIE_NAME
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


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Return the logged-in user, or None while no accounts exist/local mode is active."""
    service = AuthService(db)
    if not service.authentication_enabled():
        return None
    user = service.user_from_token(request.cookies.get(SESSION_COOKIE_NAME))
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_meeting_access(
    meeting_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> Meeting:
    """Authorize a meeting path parameter without leaking other users' resources."""
    meeting = db.get(Meeting, meeting_id)
    if meeting is None or meeting.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    auth = AuthService(db)
    if not auth.authentication_enabled():
        return meeting
    user = auth.user_from_token(request.cookies.get(SESSION_COOKIE_NAME))
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    if meeting.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


def require_job_access(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> ProcessingJob:
    """Authorize a durable job through its parent meeting."""
    job = db.get(ProcessingJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    auth = AuthService(db)
    if not auth.authentication_enabled():
        return job
    user = auth.user_from_token(request.cookies.get(SESSION_COOKIE_NAME))
    meeting = db.get(Meeting, job.meeting_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    if meeting is None or meeting.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
