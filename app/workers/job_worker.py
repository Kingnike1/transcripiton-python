"""Durable database-backed worker loop."""

import logging
import socket
import time
from collections.abc import Callable
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.enums import JobType
from app.database.session import SessionLocal
from app.models.processing_job import ProcessingJob
from app.services.persistent_job_service import PersistentJobService

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int], None]
JobHandler = Callable[[ProcessingJob, ProgressCallback], Optional[dict[str, Any]]]
SessionFactory = Callable[[], Session]


class JobWorker:
    """Claim and execute durable jobs in a process separate from FastAPI."""

    def __init__(
        self,
        handlers: Optional[dict[JobType, JobHandler]] = None,
        worker_id: Optional[str] = None,
        lease_seconds: int = 60,
        retry_delay_seconds: int = 5,
        session_factory: SessionFactory = SessionLocal,
    ) -> None:
        self.handlers = handlers or {}
        self.worker_id = worker_id or f"{socket.gethostname()}-{uuid4().hex[:8]}"
        self.lease_seconds = max(10, lease_seconds)
        self.retry_delay_seconds = max(0, retry_delay_seconds)
        self.session_factory = session_factory

    def register_handler(self, job_type: JobType, handler: JobHandler) -> None:
        self.handlers[job_type] = handler

    def run_once(self) -> bool:
        """Claim and process at most one supported job."""
        if not self.handlers:
            return False

        session = self.session_factory()
        try:
            service = PersistentJobService(session)
            job: ProcessingJob | None = None
            for job_type in self.handlers:
                job = service.claim_next(
                    self.worker_id,
                    lease_seconds=self.lease_seconds,
                    job_type=job_type,
                )
                if job is not None:
                    break
            if job is None:
                return False

            job_type = JobType(job.job_type)
            handler = self.handlers[job_type]
            try:
                def report_progress(progress: int) -> None:
                    if not service.set_progress(job.id, self.worker_id, progress):
                        raise RuntimeError("Worker lost ownership of the job")
                    service.heartbeat(job.id, self.worker_id)

                result = handler(job, report_progress)
                if not service.complete(job.id, self.worker_id, result=result):
                    raise RuntimeError("Worker lost ownership before completion")
                logger.info("Completed job %s type=%s", job.id, job.job_type)
            except Exception as exc:
                logger.exception("Job %s failed", job.id)
                service.fail_or_retry(
                    job.id,
                    self.worker_id,
                    str(exc),
                    retry_delay_seconds=self.retry_delay_seconds,
                )
            return True
        finally:
            session.close()

    def run_forever(self, poll_seconds: float = 1.0) -> None:
        logger.info("Worker %s started", self.worker_id)
        try:
            while True:
                claimed = self.run_once()
                if not claimed:
                    time.sleep(max(0.1, poll_seconds))
        except KeyboardInterrupt:
            logger.info("Worker %s stopping", self.worker_id)
