"""Worker handler for structured LLM analysis jobs."""

from typing import Any

from sqlalchemy.orm import Session

from app.core.enums import ProcessingStatus
from app.database.session import SessionLocal
from app.models.processing_job import ProcessingJob
from app.services.analysis_service import AnalysisService, LLMProvider
from app.services.meeting_service import MeetingService
from app.workers.job_worker import ProgressCallback, SessionFactory


class AnalysisJobHandler:
    """Bridge durable SUMMARIZE jobs to an LLM provider."""

    def __init__(
        self,
        provider: LLMProvider,
        provider_name: str = "ollama",
        session_factory: SessionFactory = SessionLocal,
    ) -> None:
        self.provider = provider
        self.provider_name = provider_name
        self.session_factory = session_factory

    def __call__(self, job: ProcessingJob, report_progress: ProgressCallback) -> dict[str, Any]:
        session = self.session_factory()
        try:
            service = AnalysisService(session)
            existing = service.get_by_meeting(job.meeting_id)
            if existing is not None:
                return {"analysis_id": existing.id}
            report_progress(10)
            row = service.analyze_and_persist(job.meeting_id, self.provider, self.provider_name)
            report_progress(95)
            return {"analysis_id": row.id, "provider": row.provider, "model": row.model_name}
        finally:
            session.close()

    def on_terminal_failure(self, job: ProcessingJob, _error: str) -> None:
        session: Session = self.session_factory()
        try:
            meeting = MeetingService(session).get_by_id(job.meeting_id)
            if meeting is None or meeting.status == ProcessingStatus.FAILED.value:
                return
            MeetingService(session).transition_status(job.meeting_id, ProcessingStatus.FAILED)
        finally:
            session.close()
