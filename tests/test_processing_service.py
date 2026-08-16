"""Tests for ProcessingService with durable jobs."""

import pytest

from app.core.enums import JobStatus, ProcessingStatus
from app.models.audio import Audio
from app.models.meeting import Meeting
from app.services.meeting_service import MeetingService
from app.services.persistent_job_service import PersistentJobService
from app.services.processing_service import ProcessingService


def _service(db_session) -> ProcessingService:
    return ProcessingService(MeetingService(db_session), PersistentJobService(db_session))


def _meeting_with_audio(db_session, status: ProcessingStatus = ProcessingStatus.AUDIO_UPLOADED):
    meeting = Meeting(title="Process me", status=status.value)
    db_session.add(meeting)
    db_session.flush()
    audio = Audio(
        meeting_id=meeting.id,
        filename="meeting.wav",
        file_path="storage/audio/process.wav",
        file_size=256,
        mime_type="audio/wav",
    )
    db_session.add(audio)
    db_session.commit()
    return meeting, audio


def test_start_transcription_creates_persistent_job_idempotently(db_session) -> None:
    meeting, audio = _meeting_with_audio(db_session)
    service = _service(db_session)

    first_id = service.start_transcription(meeting.id, audio.id)
    second_id = service.start_transcription(meeting.id, audio.id)

    assert first_id == second_id
    job = PersistentJobService(db_session).get_job(first_id)
    assert job is not None
    assert job.status == JobStatus.PENDING.value
    assert job.payload == {"audio_id": audio.id}


def test_start_transcription_rejects_missing_meeting(db_session) -> None:
    with pytest.raises(ValueError, match="Meeting not found"):
        _service(db_session).start_transcription(999, 1)


def test_start_transcription_rejects_wrong_meeting_status(db_session) -> None:
    meeting, audio = _meeting_with_audio(db_session, ProcessingStatus.CREATED)
    with pytest.raises(ValueError, match="not ready for transcription"):
        _service(db_session).start_transcription(meeting.id, audio.id)


def test_processing_status_reports_durable_job(db_session) -> None:
    meeting, audio = _meeting_with_audio(db_session)
    service = _service(db_session)
    job_id = service.start_transcription(meeting.id, audio.id)

    status = service.get_processing_status(meeting.id)

    assert status["meeting_id"] == meeting.id
    assert status["current_status"] == ProcessingStatus.AUDIO_UPLOADED.value
    jobs = status["jobs"]
    assert isinstance(jobs, list)
    assert jobs[0]["id"] == job_id
    assert jobs[0]["status"] == JobStatus.PENDING.value
    assert jobs[0]["progress"] == 0


def test_processing_status_returns_error_for_unknown_meeting(db_session) -> None:
    assert _service(db_session).get_processing_status(999) == {"error": "Meeting not found"}


def test_mark_transcribing_and_failed_persist(db_session) -> None:
    meeting, _audio = _meeting_with_audio(db_session)
    service = _service(db_session)

    assert service.mark_transcribing(meeting.id) is True
    db_session.expire_all()
    assert MeetingService(db_session).get_by_id(meeting.id).status == ProcessingStatus.TRANSCRIBING.value

    assert service.mark_failed(meeting.id, "provider failed") is True
    db_session.expire_all()
    assert MeetingService(db_session).get_by_id(meeting.id).status == ProcessingStatus.FAILED.value
