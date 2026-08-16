"""Tests for JobService."""

import pytest

from app.core.enums import JobStatus, JobType
from app.services.job_service import Job, JobService


class TestJobService:
    @pytest.fixture
    def job_service(self):
        return JobService()

    def test_create_job(self, job_service):
        job = job_service.create_job(JobType.TRANSCRIBE, meeting_id=1)
        assert job.id is not None
        assert job.type == JobType.TRANSCRIBE
        assert job.meeting_id == 1
        assert job.status == JobStatus.PENDING

    def test_get_job(self, job_service):
        created = job_service.create_job(JobType.TRANSCRIBE)
        retrieved = job_service.get_job(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_job_not_found(self, job_service):
        assert job_service.get_job("nonexistent") is None

    def test_get_jobs_by_meeting(self, job_service):
        job_service.create_job(JobType.TRANSCRIBE, meeting_id=1)
        job_service.create_job(JobType.DIARIZE, meeting_id=1)
        job_service.create_job(JobType.SUMMARIZE, meeting_id=2)
        assert len(job_service.get_jobs_by_meeting(1)) == 2

    def test_get_active_jobs(self, job_service):
        job1 = job_service.create_job(JobType.TRANSCRIBE)
        job_service.create_job(JobType.DIARIZE)
        job1.start()
        assert len(job_service.get_active_jobs()) == 2

    def test_get_pending_jobs(self, job_service):
        job1 = job_service.create_job(JobType.TRANSCRIBE)
        job2 = job_service.create_job(JobType.DIARIZE)
        job1.start()
        pending = job_service.get_pending_jobs()
        assert len(pending) == 1
        assert pending[0].id == job2.id

    def test_cancel_pending_job(self, job_service):
        job = job_service.create_job(JobType.TRANSCRIBE)
        assert job_service.cancel_job(job.id) is True
        assert job.status == JobStatus.CANCELLED

    def test_cancel_running_job(self, job_service):
        job = job_service.create_job(JobType.TRANSCRIBE)
        job.start()
        assert job_service.cancel_job(job.id) is False

    def test_process_next_job_no_handler(self, job_service):
        job_service.create_job(JobType.TRANSCRIBE)
        job = job_service.process_next_job()
        assert job is not None
        assert job.status == JobStatus.FAILED
        assert "No handler" in job.error_message

    def test_process_next_job_with_handler(self, job_service):
        def handler(job):
            return {"result": "done"}

        job_service.register_handler(JobType.TRANSCRIBE, handler)
        job_service.create_job(JobType.TRANSCRIBE, meeting_id=1)
        job = job_service.process_next_job()
        assert job is not None
        assert job.status == JobStatus.COMPLETED
        assert job.result == {"result": "done"}

    def test_process_next_job_no_pending(self, job_service):
        assert job_service.process_next_job() is None

    def test_get_job_stats(self, job_service):
        job_service.create_job(JobType.TRANSCRIBE)
        job_service.create_job(JobType.DIARIZE)
        stats = job_service.get_job_stats()
        assert stats["total"] == 2
        assert stats["pending"] == 2
        assert stats["completed"] == 0


class TestJob:
    def test_start(self):
        job = Job(type=JobType.TRANSCRIBE)
        job.start()
        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None

    def test_complete(self):
        job = Job(type=JobType.TRANSCRIBE)
        job.complete({"data": "result"})
        assert job.status == JobStatus.COMPLETED
        assert job.completed_at is not None
        assert job.result == {"data": "result"}

    def test_fail(self):
        job = Job(type=JobType.TRANSCRIBE)
        job.fail("Something went wrong")
        assert job.status == JobStatus.FAILED
        assert job.completed_at is not None
        assert job.error_message == "Something went wrong"

    def test_cancel(self):
        job = Job(type=JobType.TRANSCRIBE)
        job.cancel()
        assert job.status == JobStatus.CANCELLED
        assert job.completed_at is not None
