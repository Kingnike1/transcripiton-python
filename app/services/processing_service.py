"""Orchestrate meeting processing status transitions and prototype jobs."""

import logging
from typing import Optional

from app.core.enums import JobType, ProcessingStatus
from app.exceptions import InvalidStatusTransitionError
from app.services.interfaces import IAISummarizer, IExporter, ISpeakerIdentifier, ITranscriber
from app.services.job_service import job_service
from app.services.meeting_service import MeetingService
from app.services.pipeline_service import pipeline_service

logger = logging.getLogger(__name__)


class ProcessingService:
    """Coordinate the current in-memory processing prototype."""

    def __init__(self, meeting_service: MeetingService) -> None:
        self.meeting_service = meeting_service

    def register_components(
        self,
        transcriber: Optional[ITranscriber] = None,
        speaker_identifier: Optional[ISpeakerIdentifier] = None,
        summarizer: Optional[IAISummarizer] = None,
        exporter: Optional[IExporter] = None,
    ) -> None:
        if transcriber:
            pipeline_service.register_transcriber(transcriber)
        if speaker_identifier:
            pipeline_service.register_speaker_identifier(speaker_identifier)
        if summarizer:
            pipeline_service.register_summarizer(summarizer)
        if exporter:
            pipeline_service.register_exporter(exporter)

    def start_processing(self, meeting_id: int, audio_path: str) -> str:
        """Transition to transcription and create a prototype in-memory job."""
        success = self.meeting_service.transition_status(
            meeting_id,
            ProcessingStatus.TRANSCRIBING,
        )
        if not success:
            current = self.meeting_service.get_by_id(meeting_id)
            raise InvalidStatusTransitionError(
                "Cannot start processing. "
                f"Current status: {current.status if current else 'unknown'}"
            )

        job = job_service.create_job(
            job_type=JobType.FULL_PIPELINE,
            meeting_id=meeting_id,
            payload={"audio_path": audio_path},
        )
        logger.info(
            "Started processing pipeline for meeting %s, job_id=%s",
            meeting_id,
            job.id,
        )
        return job.id

    def handle_transcription_complete(self, meeting_id: int) -> bool:
        return self.meeting_service.transition_status(
            meeting_id,
            ProcessingStatus.DIARIZING,
        )

    def handle_diarization_complete(self, meeting_id: int) -> bool:
        return self.meeting_service.transition_status(
            meeting_id,
            ProcessingStatus.SUMMARIZING,
        )

    def handle_summarization_complete(self, meeting_id: int) -> bool:
        return self.meeting_service.transition_status(
            meeting_id,
            ProcessingStatus.COMPLETED,
        )

    def handle_processing_error(self, meeting_id: int, error_message: str) -> bool:
        success = self.meeting_service.transition_status(
            meeting_id,
            ProcessingStatus.FAILED,
        )
        if success:
            logger.error("Meeting %s processing failed: %s", meeting_id, error_message)
        return success

    def retry_processing(self, meeting_id: int) -> bool:
        return self.meeting_service.transition_status(
            meeting_id,
            ProcessingStatus.AUDIO_UPLOADED,
        )

    def get_processing_status(self, meeting_id: int) -> dict[str, object]:
        meeting = self.meeting_service.get_by_id(meeting_id)
        if not meeting:
            return {"error": "Meeting not found"}

        current_status = ProcessingStatus(meeting.status)
        jobs = job_service.get_jobs_by_meeting(meeting_id)
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
                    "type": job.type.value,
                    "status": job.status.value,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                }
                for job in jobs
            ],
            "pipeline_ready": pipeline_service.get_pipeline_status()["ready"],
        }

    def mark_audio_uploaded(self, meeting_id: int) -> bool:
        return self.meeting_service.transition_status(
            meeting_id,
            ProcessingStatus.AUDIO_UPLOADED,
        )

    def mark_recording(self, meeting_id: int) -> bool:
        return self.meeting_service.transition_status(
            meeting_id,
            ProcessingStatus.RECORDING,
        )
