"""Application service for durable background jobs."""

from datetime import timedelta
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import JobStatus, JobType
from app.core.time import utc_now
from app.database.processing_job_repository import ProcessingJobRepository
from app.database.unit_of_work import SqlAlchemyUnitOfWork
from app.models.processing_job import ProcessingJob


class PersistentJobService:
    """Own job transactions and lifecycle transitions."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.uow = SqlAlchemyUnitOfWork(session)
        self.repository = ProcessingJobRepository(session)

    def create_job(
        self,
        meeting_id: int,
        job_type: JobType,
        payload: Optional[dict[str, Any]] = None,
        max_attempts: int = 3,
    ) -> ProcessingJob:
        """Create a job idempotently while another active job exists."""
        active = self.repository.get_active(meeting_id, job_type)
        if active is not None:
            return active

        job = ProcessingJob(
            id=str(uuid4()),
            meeting_id=meeting_id,
            job_type=job_type.value,
            status=JobStatus.PENDING.value,
            payload=payload or {},
            max_attempts=max(1, max_attempts),
            available_at=utc_now(),
        )
        try:
            with self.uow.transaction():
                self.repository.create(job)
        except IntegrityError:
            self.session.rollback()
            existing = self.repository.get_active(meeting_id, job_type)
            if existing is not None:
                return existing
            raise
        self.uow.refresh(job)
        return job

    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        return self.repository.get_by_id(job_id)

    def get_jobs_by_meeting(self, meeting_id: int) -> list[ProcessingJob]:
        return self.repository.get_by_meeting(meeting_id)

    def claim_next(self, worker_id: str, lease_seconds: int = 60) -> Optional[ProcessingJob]:
        with self.uow.transaction():
            job = self.repository.claim_next(worker_id=worker_id, lease_seconds=lease_seconds)
        return job

    def heartbeat(self, job_id: str, worker_id: str) -> bool:
        with self.uow.transaction():
            return self.repository.heartbeat(job_id, worker_id)

    def set_progress(self, job_id: str, worker_id: str, progress: int) -> bool:
        job = self.repository.get_by_id(job_id)
        if job is None or job.status != JobStatus.RUNNING.value or job.locked_by != worker_id:
            return False
        with self.uow.transaction():
            job.progress = max(0, min(100, progress))
            job.updated_at = utc_now()
            self.session.flush()
        return True

    def complete(
        self,
        job_id: str,
        worker_id: str,
        result: Optional[dict[str, Any]] = None,
    ) -> bool:
        job = self.repository.get_by_id(job_id)
        if job is None or job.status != JobStatus.RUNNING.value or job.locked_by != worker_id:
            return False
        with self.uow.transaction():
            now = utc_now()
            job.status = JobStatus.COMPLETED.value
            job.progress = 100
            job.result = result
            job.error_message = None
            job.completed_at = now
            job.updated_at = now
            job.locked_by = None
            job.locked_at = None
            job.heartbeat_at = None
            self.session.flush()
        return True

    def fail_or_retry(
        self,
        job_id: str,
        worker_id: str,
        error_message: str,
        retry_delay_seconds: int = 5,
    ) -> bool:
        job = self.repository.get_by_id(job_id)
        if job is None or job.status != JobStatus.RUNNING.value or job.locked_by != worker_id:
            return False
        with self.uow.transaction():
            now = utc_now()
            job.error_message = error_message[:4000]
            job.locked_by = None
            job.locked_at = None
            job.heartbeat_at = None
            job.updated_at = now
            if job.attempt < job.max_attempts:
                job.status = JobStatus.RETRYING.value
                job.available_at = now + timedelta(seconds=max(0, retry_delay_seconds))
            else:
                job.status = JobStatus.FAILED.value
                job.completed_at = now
            self.session.flush()
        return True

    def cancel(self, job_id: str) -> bool:
        job = self.repository.get_by_id(job_id)
        if job is None or job.status not in {JobStatus.PENDING.value, JobStatus.RETRYING.value}:
            return False
        with self.uow.transaction():
            now = utc_now()
            job.status = JobStatus.CANCELLED.value
            job.completed_at = now
            job.updated_at = now
            self.session.flush()
        return True
