"""Persistence operations for durable processing jobs."""

from datetime import timedelta
from typing import Optional

from sqlalchemy import and_, or_, select, update
from sqlalchemy.orm import Session

from app.core.enums import JobStatus, JobType
from app.core.time import utc_now
from app.models.processing_job import ProcessingJob


class ProcessingJobRepository:
    """Transaction-neutral repository for ProcessingJob."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, job_id: str) -> Optional[ProcessingJob]:
        return self.session.get(ProcessingJob, job_id)

    def get_by_meeting(self, meeting_id: int, limit: int = 50) -> list[ProcessingJob]:
        stmt = (
            select(ProcessingJob)
            .where(ProcessingJob.meeting_id == meeting_id)
            .order_by(ProcessingJob.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def get_active(self, meeting_id: int, job_type: JobType) -> Optional[ProcessingJob]:
        stmt = (
            select(ProcessingJob)
            .where(
                ProcessingJob.meeting_id == meeting_id,
                ProcessingJob.job_type == job_type.value,
                ProcessingJob.status.in_(
                    [
                        JobStatus.PENDING.value,
                        JobStatus.RUNNING.value,
                        JobStatus.RETRYING.value,
                    ]
                ),
            )
            .order_by(ProcessingJob.created_at.desc())
            .limit(1)
        )
        return self.session.scalar(stmt)

    def create(self, job: ProcessingJob) -> ProcessingJob:
        self.session.add(job)
        self.session.flush()
        return job

    def claim_next(
        self,
        worker_id: str,
        lease_seconds: int,
        job_type: JobType | None = None,
    ) -> Optional[ProcessingJob]:
        """Optimistically claim one available job without relying on process locks."""
        now = utc_now()
        stale_before = now - timedelta(seconds=lease_seconds)
        filters = [
            ProcessingJob.available_at <= now,
            or_(
                ProcessingJob.status.in_([JobStatus.PENDING.value, JobStatus.RETRYING.value]),
                and_(
                    ProcessingJob.status == JobStatus.RUNNING.value,
                    or_(
                        ProcessingJob.heartbeat_at.is_(None),
                        ProcessingJob.heartbeat_at < stale_before,
                    ),
                ),
            ),
        ]
        if job_type is not None:
            filters.append(ProcessingJob.job_type == job_type.value)

        candidates = list(
            self.session.scalars(
                select(ProcessingJob)
                .where(*filters)
                .order_by(ProcessingJob.available_at.asc(), ProcessingJob.created_at.asc())
                .limit(10)
            )
        )

        for candidate in candidates:
            previous_status = candidate.status
            previous_heartbeat = candidate.heartbeat_at
            conditions = [ProcessingJob.id == candidate.id, ProcessingJob.status == previous_status]
            if previous_status == JobStatus.RUNNING.value:
                if previous_heartbeat is None:
                    conditions.append(ProcessingJob.heartbeat_at.is_(None))
                else:
                    conditions.append(ProcessingJob.heartbeat_at == previous_heartbeat)

            result = self.session.execute(
                update(ProcessingJob)
                .where(*conditions)
                .values(
                    status=JobStatus.RUNNING.value,
                    locked_by=worker_id,
                    locked_at=now,
                    heartbeat_at=now,
                    started_at=ProcessingJob.started_at if previous_status == JobStatus.RUNNING.value else now,
                    attempt=ProcessingJob.attempt + 1,
                    updated_at=now,
                )
            )
            if result.rowcount == 1:
                self.session.flush()
                return self.session.get(ProcessingJob, candidate.id, populate_existing=True)

            self.session.expire_all()

        return None

    def heartbeat(self, job_id: str, worker_id: str) -> bool:
        now = utc_now()
        result = self.session.execute(
            update(ProcessingJob)
            .where(
                ProcessingJob.id == job_id,
                ProcessingJob.status == JobStatus.RUNNING.value,
                ProcessingJob.locked_by == worker_id,
            )
            .values(heartbeat_at=now, updated_at=now)
        )
        self.session.flush()
        return result.rowcount == 1
