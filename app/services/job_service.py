"""
Job service module.
Manages background job processing queue.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from uuid import uuid4

from app.core.enums import JobStatus, JobType

logger = logging.getLogger(__name__)


@dataclass
class Job:
    """Represents a background processing job.
    
    Attributes:
        id: Unique job identifier
        type: Type of job
        status: Current job status
        meeting_id: Associated meeting ID
        payload: Job-specific data
        created_at: Job creation timestamp
        started_at: Job start timestamp
        completed_at: Job completion timestamp
        error_message: Error details if failed
        result: Job result data
    """
    
    id: str = field(default_factory=lambda: str(uuid4()))
    type: JobType = JobType.FULL_PIPELINE
    status: JobStatus = JobStatus.PENDING
    meeting_id: Optional[int] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
    def start(self) -> None:
        """Mark job as running."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)
    
    def complete(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark job as completed.
        
        Args:
            result: Optional job result data
        """
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.result = result
    
    def fail(self, error_message: str) -> None:
        """Mark job as failed.
        
        Args:
            error_message: Description of the error
        """
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.error_message = error_message
    
    def cancel(self) -> None:
        """Mark job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)


class JobService:
    """Service for managing background jobs.
    
    Provides a job queue for async processing tasks.
    Jobs are processed in order of creation (FIFO).
    
    In production, this would be replaced with a proper
    task queue (e.g., Celery, RQ, Dramatiq).
    """
    
    def __init__(self):
        """Initialize job service."""
        self._jobs: Dict[str, Job] = {}
        self._handlers: Dict[JobType, Callable] = {}
    
    def register_handler(self, job_type: JobType, handler: Callable) -> None:
        """Register a handler function for a job type.
        
        Args:
            job_type: Job type to handle
            handler: Handler function that processes the job
        """
        self._handlers[job_type] = handler
        logger.info(f"Registered handler for job type: {job_type}")
    
    def create_job(
        self,
        job_type: JobType,
        meeting_id: Optional[int] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Job:
        """Create a new job.
        
        Args:
            job_type: Type of job to create
            meeting_id: Associated meeting ID
            payload: Job-specific data
            
        Returns:
            Created Job instance
        """
        job = Job(
            type=job_type,
            meeting_id=meeting_id,
            payload=payload or {},
        )
        
        self._jobs[job.id] = job
        logger.info(
            f"Created job: {job.id} (type={job_type}, meeting_id={meeting_id})"
        )
        
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job instance if found, None otherwise
        """
        return self._jobs.get(job_id)
    
    def get_jobs_by_meeting(self, meeting_id: int) -> List[Job]:
        """Get all jobs for a specific meeting.
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            List of jobs for the meeting
        """
        return [
            job for job in self._jobs.values()
            if job.meeting_id == meeting_id
        ]
    
    def get_active_jobs(self) -> List[Job]:
        """Get all active (non-terminal) jobs.
        
        Returns:
            List of active jobs
        """
        return [
            job for job in self._jobs.values()
            if job.status in [JobStatus.PENDING, JobStatus.RUNNING]
        ]
    
    def get_pending_jobs(self) -> List[Job]:
        """Get all pending jobs.
        
        Returns:
            List of pending jobs
        """
        return [
            job for job in self._jobs.values()
            if job.status == JobStatus.PENDING
        ]
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancelled, False if not found or already running
        """
        job = self.get_job(job_id)
        
        if job and job.status == JobStatus.PENDING:
            job.cancel()
            logger.info(f"Cancelled job: {job_id}")
            return True
        
        return False
    
    def process_next_job(self) -> Optional[Job]:
        """Process the next pending job.
        
        Finds the next pending job and executes its handler.
        In production, this would be called by a worker process.
        
        Returns:
            Processed Job instance, or None if no jobs pending
        """
        pending_jobs = self.get_pending_jobs()
        
        if not pending_jobs:
            return None
        
        # Process oldest job first (FIFO)
        job = min(pending_jobs, key=lambda j: j.created_at)
        
        handler = self._handlers.get(job.type)
        
        if handler is None:
            job.fail(f"No handler registered for job type: {job.type}")
            logger.error(f"No handler for job type: {job.type}")
            return job
        
        job.start()
        logger.info(f"Processing job: {job.id} (type={job.type})")
        
        try:
            result = handler(job)
            job.complete(result)
            logger.info(f"Completed job: {job.id}")
        except Exception as e:
            job.fail(str(e))
            logger.error(f"Failed job: {job.id} - {e}")
        
        return job
    
    def get_job_stats(self) -> Dict[str, int]:
        """Get job statistics.
        
        Returns:
            Dictionary with job counts by status
        """
        stats = {
            "total": len(self._jobs),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }
        
        for job in self._jobs.values():
            stats[job.status.value.lower()] += 1
        
        return stats


# Singleton instance
job_service = JobService()
