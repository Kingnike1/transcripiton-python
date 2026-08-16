"""Durable database-backed worker loop."""

import logging
import socket
import time
from collections.abc import Callable
from threading import Event, Thread
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.enums import JobStatus, JobType
from app.database.session import SessionLocal
from app.models.processing_job import ProcessingJob
from app.services.persistent_job_service import PersistentJobService

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int], None]
JobHandler = Callable[[ProcessingJob, ProgressCallback], Optional[dict[str, Any]]]
FailureHandler = Callable[[ProcessingJob, str], None]
SessionFactory = Callable[[], Session]


class JobWorker:
    """Claim and execute durable jobs in a process separate from FastAPI."""

    def __init__(
        self,
        handlers: Optional[dict[JobType, JobHandler]] = None,
        failure_handlers: Optional[dict[JobType, FailureHandler]] = None,
        worker_id: Optional[str] = None,
        lease_seconds: int = 60,
        retry_delay_seconds: int = 5,
        session_factory: SessionFactory = SessionLocal,
    ) -> None:
        self.handlers = handlers or {}
        self.failure_handlers = failure_handlers or {}
        self.worker_id = worker_id or f"{socket.gethostname()}-{uuid4().hex[:8]}"
        self.lease_seconds = max(10, lease_seconds)
        self.retry_delay_seconds = max(0, retry_delay_seconds)
        self.session_factory = session_factory

    def register_handler(
        self,
        job_type: JobType,
        handler: JobHandler,
        on_terminal_failure: Optional[FailureHandler] = None,
    ) -> None:
        self.handlers[job_type] = handler
        if on_terminal_failure is not None:
            self.failure_handlers[job_type] = on_terminal_failure

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
            heartbeat_stop, heartbeat_thread = self._start_heartbeat(job.id)
            try:
                def report_progress(progress: int) -> None:
                    if not service.set_progress(job.id, self.worker_id, progress):
                        raise RuntimeError("Worker lost ownership of the job")

                result = handler(job, report_progress)
                heartbeat_stop.set()
                heartbeat_thread.join(timeout=2)
                if not service.complete(job.id, self.worker_id, result=result):
                    raise RuntimeError("Worker lost ownership before completion")
                logger.info("Completed job %s type=%s", job.id, job.job_type)
            except Exception as exc:
                heartbeat_stop.set()
                heartbeat_thread.join(timeout=2)
                logger.exception("Job %s failed", job.id)
                if not service.fail_or_retry(
                    job.id,
                    self.worker_id,
                    str(exc),
                    retry_delay_seconds=self.retry_delay_seconds,
                ):
                    return True
                session.expire_all()
                persisted = service.get_job(job.id)
                if persisted is not None and persisted.status == JobStatus.FAILED.value:
                    failure_handler = self.failure_handlers.get(job_type)
                    if failure_handler is not None:
                        failure_handler(persisted, str(exc))
            return True
        finally:
            session.close()

    def _start_heartbeat(self, job_id: str) -> tuple[Event, Thread]:
        stop = Event()
        interval = max(2.0, self.lease_seconds / 3)

        def loop() -> None:
            while not stop.wait(interval):
                heartbeat_session = self.session_factory()
                try:
                    service = PersistentJobService(heartbeat_session)
                    if not service.heartbeat(job_id, self.worker_id):
                        logger.warning("Worker %s lost heartbeat ownership for %s", self.worker_id, job_id)
                        return
                except Exception:
                    logger.exception("Heartbeat failed for job %s", job_id)
                finally:
                    heartbeat_session.close()

        thread = Thread(target=loop, name=f"job-heartbeat-{job_id[:8]}", daemon=True)
        thread.start()
        return stop, thread

    def run_forever(self, poll_seconds: float = 1.0) -> None:
        logger.info("Worker %s started", self.worker_id)
        try:
            while True:
                claimed = self.run_once()
                if not claimed:
                    time.sleep(max(0.1, poll_seconds))
        except KeyboardInterrupt:
            logger.info("Worker %s stopping", self.worker_id)
