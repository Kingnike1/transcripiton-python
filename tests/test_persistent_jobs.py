"""Tests for durable job persistence, claiming and recovery."""

from datetime import timedelta

from sqlalchemy.orm import sessionmaker

from app.core.enums import JobStatus, JobType, ProcessingStatus
from app.core.time import utc_now
from app.models.audio import Audio
from app.models.meeting import Meeting
from app.services.persistent_job_service import PersistentJobService
from app.workers.job_worker import JobWorker


def _meeting_with_audio(db_session) -> Meeting:
    meeting = Meeting(title="Persistent jobs", status=ProcessingStatus.AUDIO_UPLOADED.value)
    db_session.add(meeting)
    db_session.flush()
    db_session.add(
        Audio(
            meeting_id=meeting.id,
            filename="meeting.wav",
            file_path="storage/audio/test.wav",
            file_size=128,
            mime_type="audio/wav",
        )
    )
    db_session.commit()
    return meeting


def test_job_is_persistent_and_idempotent(db_session) -> None:
    meeting = _meeting_with_audio(db_session)
    service = PersistentJobService(db_session)

    first = service.create_job(meeting.id, JobType.TRANSCRIBE, {"audio_id": 1})
    second = service.create_job(meeting.id, JobType.TRANSCRIBE, {"audio_id": 1})

    assert second.id == first.id
    db_session.close()

    SessionFactory = sessionmaker(bind=db_session.get_bind())
    fresh = SessionFactory()
    try:
        persisted = PersistentJobService(fresh).get_job(first.id)
        assert persisted is not None
        assert persisted.status == JobStatus.PENDING.value
    finally:
        fresh.close()


def test_stale_running_job_can_be_reclaimed(db_session) -> None:
    meeting = _meeting_with_audio(db_session)
    service = PersistentJobService(db_session)
    job = service.create_job(meeting.id, JobType.TRANSCRIBE)

    claimed = service.claim_next("worker-a", lease_seconds=60)
    assert claimed is not None
    assert claimed.id == job.id
    assert claimed.attempt == 1

    claimed.heartbeat_at = utc_now() - timedelta(seconds=120)
    db_session.commit()

    reclaimed = service.claim_next("worker-b", lease_seconds=60)
    assert reclaimed is not None
    assert reclaimed.id == job.id
    assert reclaimed.locked_by == "worker-b"
    assert reclaimed.attempt == 2


def test_retry_exhaustion_becomes_failed(db_session) -> None:
    meeting = _meeting_with_audio(db_session)
    service = PersistentJobService(db_session)
    job = service.create_job(meeting.id, JobType.TRANSCRIBE, max_attempts=2)

    assert service.claim_next("worker-a") is not None
    assert service.fail_or_retry(job.id, "worker-a", "temporary", retry_delay_seconds=0)
    db_session.expire_all()
    assert service.get_job(job.id).status == JobStatus.RETRYING.value

    assert service.claim_next("worker-b") is not None
    assert service.fail_or_retry(job.id, "worker-b", "permanent", retry_delay_seconds=0)
    db_session.expire_all()
    failed = service.get_job(job.id)
    assert failed.status == JobStatus.FAILED.value
    assert failed.attempt == 2


def test_worker_completes_job_with_progress(db_session) -> None:
    meeting = _meeting_with_audio(db_session)
    job = PersistentJobService(db_session).create_job(meeting.id, JobType.TRANSCRIBE)
    SessionFactory = sessionmaker(bind=db_session.get_bind())

    def handler(_job, report_progress):
        report_progress(50)
        return {"ok": True}

    worker = JobWorker(
        handlers={JobType.TRANSCRIBE: handler},
        worker_id="worker-test",
        session_factory=SessionFactory,
    )
    assert worker.run_once() is True

    db_session.expire_all()
    completed = PersistentJobService(db_session).get_job(job.id)
    assert completed.status == JobStatus.COMPLETED.value
    assert completed.progress == 100
    assert completed.result == {"ok": True}


def test_jobs_api_is_idempotent(client, db_session) -> None:
    meeting = _meeting_with_audio(db_session)

    first = client.post(f"/api/meetings/{meeting.id}/jobs/transcription")
    second = client.post(f"/api/meetings/{meeting.id}/jobs/transcription")

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]

    fetched = client.get(f"/api/jobs/{first.json()['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == JobStatus.PENDING.value
