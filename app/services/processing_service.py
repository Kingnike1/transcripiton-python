"""Coordinate meeting processing with durable jobs."""

import logging

from app.core.enums import JobType, ProcessingStatus
from app.services.meeting_service import MeetingService
from app.services.persistent_job_service import PersistentJobService

logger = logging.getLogger(__name__)


class ProcessingService:
    """Coordinate meeting status and durable processing jobs."""

    def __init__(
        self,
        meeting_service: MeetingService,
        job_service: PersistentJobService,
    ) -> None:
        self.meeting_service = meeting_service
        self.job_service = job_service

    def start_transcription(self, meeting_id: int, audio_id: int) -> str:
        """Create or return the active transcription job for a meeting."""
        meeting = self.meeting_service.get_by_id(meeting_id)
        if meeting is None:
            raise ValueError("Meeting not found")
        if meeting.status != ProcessingStatus.AUDIO_UPLOADED.value:
            raise ValueError(f"Meeting is not ready for transcription: {meeting.status}")

        job = self.job_service.create_job(
            meeting_id=meeting_id,
            job_type=JobType.TRANSCRIBE,
            payload={"audio_id": audio_id},
        )
        logger.info("Queued transcription for meeting %s job_id=%s", meeting_id, job.id)
        return job.id

    def get_processing_status(self, meeting_id: int) -> dict[str, object]:
        meeting = self.meeting_service.get_by_id(meeting_id)
        if meeting is None:
            return {"error": "Meeting not found"}

        current_status = ProcessingStatus(meeting.status)
        jobs = self.job_service.get_jobs_by_meeting(meeting_id)
        return {
            "meeting_id": meeting.id,
            "title": meeting.title,
            "current_status": meeting.status,
            "is_terminal": current_status in ProcessingStatus.terminal_states(),
            "is_active": current_status in ProcessingStatus.active_states(),
            "is_processing": current_status in ProcessingStatus.processing_states(),
            "jobs": [
                {
                    "id": job.id,
                    "type": job.job_type,
                    "status": job.status,
                    "progress": job.progress,
                    "attempt": job.attempt,
                    "created_at": job.created_at.isoformat(),
                }
                for job in jobs
            ],
        }

    def mark_transcribing(self, meeting_id: int) -> bool:
        return self.meeting_service.transition_status(meeting_id, ProcessingStatus.TRANSCRIBING)

    def mark_failed(self, meeting_id: int, error_message: str) -> bool:
        success = self.meeting_service.transition_status(meeting_id, ProcessingStatus.FAILED)
        if success:
            logger.error("Meeting %s processing failed: %s", meeting_id, error_message)
        return success
