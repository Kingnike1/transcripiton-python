"""
Tests for JobService.
"""

import pytest

from app.core.enums import JobStatus, JobType
from app.services.job_service import JobService, Job


class TestJobService:
    """Tests for JobService."""
    
    @pytest.fixture
    def job_service(self):
        """Create fresh job service instance."""
        return JobService()
    
    def test_create_job(self, job_service):
        """Test creating a new job."""
        job = job_service.create_job(JobType.TRANSCRIBE, meeting_id=1)
        
        assert job is not None
        assert job.id is not None
        assert job.type == JobType.TRANSCRIBE
        assert job.meeting_id == 1
        assert job.status == JobStatus.PENDING
    
    def test_get_job(self, job_service):
        """Test getting a job by ID."""
        created = job_service.create_job(JobType.TRANSCRIBE)
        
        retrieved = job_service.get_job(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
    
    def test_get_job_not_found(self, job_service):
        """Test getting a non-existent job."""
        job = job_service.get_job("nonexistent")
        assert job is None
    
    def test_get_jobs_by_meeting(self, job_service):
        """Test getting jobs by meeting ID."""
        job_service.create_job(JobType.TRANSCRIBE, meeting_id=1)
        job_service.create_job(JobType.DIARIZE, meeting_id=1)
        job_service.create_job(JobType.SUMMARIZE, meeting_id=2)
        
        jobs = job_service.get_jobs_by_meeting(1)
        
        assert len(jobs) == 2
    
    def test_get_active_jobs(self, job_service):
        """Test getting active jobs."""
        job1 = job_service.create_job(JobType.TRANSCRIBE)
        job2 = job_service.create_job(JobType.DIARIZE)
        job1.start()
        
        active = job_service.get_active_jobs()
        
        assert len(active) == 2  # PENDING + RUNNING
    
    def test_get_pending_jobs(self, job_service):
        """Test getting pending jobs."""
        job1 = job_service.create_job(JobType.TRANSCRIBE)
        job2 = job_service.create_job(JobType.DIARIZE)
        job1.start()
        
        pending = job_service.get_pending_jobs()
        
        assert len(pending) == 1
        assert pending[0].id == job2.id
    
    def test_cancel_pending_job(self, job_service):
        """Test cancelling a pending job."""
        job = job_service.create_job(JobType.TRANSCRIBE)
        
        result = job_service.cancel_job(job.id)
        
        assert result is True
        assert job.status == JobStatus.CANCELLED
    
    def test_cancel_running_job(self, job_service):
        """Test that running jobs cannot be cancelled."""
        job = job_service.create_job(JobType.TRANSCRIBE)
        job.start()
        
        result = job_service.cancel_job(job.id)
        
        assert result is False
    
    def test_process_next_job_no_handler(self, job_service):
        """Test processing job with no handler."""
        job_service.create_job(JobType.TRANSCRIBE)
        
        job = job_service.process_next_job()
        
        assert job is not None
        assert job.status == JobStatus.FAILED
        assert "No handler" in job.error_message
    
    def test_process_next_job_with_handler(self, job_service):
        """Test processing job with handler."""
        # Register handler
        def handler(job):
            return {"result": "done"}
        
        job_service.register_handler(JobType.TRANSCRIBE, handler)
        
        # Create and process
        job_service.create_job(JobType.TRANSCRIBE, meeting_id=1)
        
        job = job_service.process_next_job()
        
        assert job is not None
        assert job.status == JobStatus.COMPLETED
        assert job.result == {"result": "done"}
    
    def test_process_next_job_no_pending(self, job_service):
        """Test processing when no jobs are pending."""
        job = job_service.process_next_job()
        assert job is None
    
    def test_get_job_stats(self, job_service):
        """Test getting job statistics."""
        job_service.create_job(JobType.TRANSCRIBE)
        job_service.create_job(JobType.DIARIZE)
        
        stats = job_service.get_job_stats()
        
        assert stats["total"] == 2
        assert stats["pending"] == 2
        assert stats["completed"] == 0


class TestJob:
    """Tests for Job dataclass."""
    
    def test_start(self):
        """Test starting a job."""
        job = Job(type=JobType.TRANSCRIBE)
        
        job.start()
        
        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None
    
    def test_complete(self):
        """Test completing a job."""
        job = Job(type=JobType.TRANSCRIBE)
        
        job.complete({"data": "result"})
        
        assert job.status == JobStatus.COMPLETED
        assert job.completed_at is not None
        assert job.result == {"data": "result"}
    
    def test_fail(self):
        """Test failing a job."""
        job = Job(type=JobType.TRANSCRIBE)
        
        job.fail("Something went wrong")
        
        assert job.status == JobStatus.FAILED
        assert job.completed_at is not None
        assert job.error_message == "Something went wrong"
    
    def test_cancel(self):
        """Test cancelling a job."""
        job = Job(type=JobType.TRANSCRIBE)
        
        job.cancel()
        
        assert job.status == JobStatus.CANCELLED
        assert job.completed_at is not None
