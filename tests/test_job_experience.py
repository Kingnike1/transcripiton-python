"""Sprint 2 tests for user-facing job lifecycle state."""

from datetime import timedelta

from app.core.enums import JobStatus, JobType, ProcessingStatus
from app.core.time import utc_now
from app.models.audio import Audio
from app.models.meeting import Meeting
from app.models.processing_job import ProcessingJob
from app.services.job_experience_service import JobExperienceService
from app.services.persistent_job_service import PersistentJobService


class FakeHeartbeat:
    def __init__(self, age: float | None) -> None:
        self.age = age

    def age_seconds(self) -> float | None:
        return self.age


def _job(status: str) -> ProcessingJob:
    now = utc_now()
    return ProcessingJob(id="job-1", meeting_id=1, job_type=JobType.TRANSCRIBE.value, status=status, progress=0, attempt=0, max_attempts=3, payload={}, available_at=now, created_at=now, updated_at=now)


def test_pending_job_is_presented_as_blocked_when_worker_is_offline() -> None:
    result = JobExperienceService(FakeHeartbeat(None)).describe(_job(JobStatus.PENDING.value))
    assert result["effective_status"] == "BLOCKED"
    assert result["blocked_reason"]
    assert result["can_cancel"] is True


def test_pending_job_remains_pending_with_recent_worker() -> None:
    result = JobExperienceService(FakeHeartbeat(2)).describe(_job(JobStatus.PENDING.value))
    assert result["effective_status"] == JobStatus.PENDING.value
    assert result["status_label"] == "Aguardando na fila"


def test_running_job_reports_stalled_after_missing_updates() -> None:
    job = _job(JobStatus.RUNNING.value)
    job.updated_at = utc_now() - timedelta(seconds=120)
    result = JobExperienceService(FakeHeartbeat(2)).describe(job)
    assert result["stalled"] is True
    assert "sem atualização" in str(result["status_label"]).lower()


def test_failed_job_can_be_explicitly_retried(db_session) -> None:
    meeting = Meeting(title="Retry UX", status=ProcessingStatus.AUDIO_UPLOADED.value)
    db_session.add(meeting)
    db_session.flush()
    db_session.add(Audio(meeting_id=meeting.id, filename="meeting.wav", file_path="storage/audio/retry.wav", file_size=128, mime_type="audio/wav"))
    db_session.commit()
    service = PersistentJobService(db_session)
    job = service.create_job(meeting.id, JobType.TRANSCRIBE, max_attempts=1)
    assert service.claim_next("worker-a") is not None
    assert service.fail_or_retry(job.id, "worker-a", "boom", retry_delay_seconds=0)
    db_session.expire_all()
    assert service.get_job(job.id).status == JobStatus.FAILED.value
    assert service.retry(job.id) is True
    db_session.expire_all()
    retried = service.get_job(job.id)
    assert retried is not None
    assert retried.status == JobStatus.PENDING.value
    assert retried.attempt == 0
    assert retried.error_message is None


def test_retry_api_rejects_non_failed_job(client, db_session) -> None:
    meeting = Meeting(title="Retry API", status=ProcessingStatus.AUDIO_UPLOADED.value)
    db_session.add(meeting)
    db_session.flush()
    db_session.add(Audio(meeting_id=meeting.id, filename="meeting.wav", file_path="storage/audio/retry-api.wav", file_size=128, mime_type="audio/wav"))
    db_session.commit()
    created = client.post(f"/api/meetings/{meeting.id}/jobs/transcription")
    assert created.status_code == 201
    response = client.post(f"/api/jobs/{created.json()['id']}/retry")
    assert response.status_code == 409
