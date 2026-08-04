"""
Processing service module.
Orchestrates meeting processing status transitions and job execution.
"""

import logging
from typing import Optional

from app.core.enums import ProcessingStatus, JobType
from app.core.exceptions import InvalidStatusTransitionError, PipelineError
from app.services.meeting_service import MeetingService
from app.services.job_service import job_service
from app.services.pipeline_service import pipeline_service
from app.services.interfaces import (
    ITranscriber,
    ISpeakerIdentifier,
    IAISummarizer,
    IExporter,
)

logger = logging.getLogger(__name__)


class ProcessingService:
    """Service for orchestrating meeting processing workflows.
    
    Manages the lifecycle of meeting processing by:
    - Coordinating status transitions
    - Creating and tracking processing jobs
    - Calling pipeline components in the correct order
    - Handling errors and retry logic
    
    This service does NOT implement any AI logic directly.
    It delegates to pipeline components registered via interfaces.
    """
    
    def __init__(self, meeting_service: MeetingService):
        """Initialize processing service.
        
        Args:
            meeting_service: Meeting service for status management
        """
        self.meeting_service = meeting_service
    
    def register_components(
        self,
        transcriber: Optional[ITranscriber] = None,
        speaker_identifier: Optional[ISpeakerIdentifier] = None,
        summarizer: Optional[IAISummarizer] = None,
        exporter: Optional[IExporter] = None,
    ) -> None:
        """Register pipeline components.
        
        Args:
            transcriber: Transcription implementation
            speaker_identifier: Speaker identification implementation
            summarizer: AI summarization implementation
            exporter: Export implementation
        """
        if transcriber:
            pipeline_service.register_transcriber(transcriber)
        if speaker_identifier:
            pipeline_service.register_speaker_identifier(speaker_identifier)
        if summarizer:
            pipeline_service.register_summarizer(summarizer)
        if exporter:
            pipeline_service.register_exporter(exporter)
    
    def start_processing(self, meeting_id: int, audio_path: str) -> str:
        """Start the full processing pipeline for a meeting.
        
        Transitions status to TRANSCRIBING and creates a job.
        
        Args:
            meeting_id: Meeting ID to process
            audio_path: Path to audio file
            
        Returns:
            Job ID for tracking
            
        Raises:
            InvalidStatusTransitionError: If meeting cannot start processing
            PipelineError: If processing cannot be started
        """
        # Transition to TRANSCRIBING
        success = self.meeting_service.transition_status(
            meeting_id, ProcessingStatus.TRANSCRIBING
        )
        
        if not success:
            current = self.meeting_service.get_by_id(meeting_id)
            raise InvalidStatusTransitionError(
                f"Cannot start processing. "
                f"Current status: {current.status if current else 'unknown'}"
            )
        
        # Create job
        job = job_service.create_job(
            job_type=JobType.FULL_PIPELINE,
            meeting_id=meeting_id,
            payload={"audio_path": audio_path},
        )
        
        logger.info(
            f"Started processing pipeline for meeting {meeting_id}, "
            f"job_id={job.id}"
        )
        
        return job.id
    
    def handle_transcription_complete(
        self, meeting_id: int
    ) -> bool:
        """Handle completion of transcription step.
        
        Transitions status from TRANSCRIBING to DIARIZING.
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            True if transition was successful
        """
        return self.meeting_service.transition_status(
            meeting_id, ProcessingStatus.DIARIZING
        )
    
    def handle_diarization_complete(
        self, meeting_id: int
    ) -> bool:
        """Handle completion of diarization step.
        
        Transitions status from DIARIZING to SUMMARIZING.
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            True if transition was successful
        """
        return self.meeting_service.transition_status(
            meeting_id, ProcessingStatus.SUMMARIZING
        )
    
    def handle_summarization_complete(
        self, meeting_id: int
    ) -> bool:
        """Handle completion of summarization step.
        
        Transitions status from SUMMARIZING to COMPLETED.
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            True if transition was successful
        """
        return self.meeting_service.transition_status(
            meeting_id, ProcessingStatus.COMPLETED
        )
    
    def handle_processing_error(
        self, meeting_id: int, error_message: str
    ) -> bool:
        """Handle a processing error at any stage.
        
        Transitions status to FAILED from any active state.
        
        Args:
            meeting_id: Meeting ID
            error_message: Description of the error
            
        Returns:
            True if transition was successful
        """
        success = self.meeting_service.transition_status(
            meeting_id, ProcessingStatus.FAILED
        )
        
        if success:
            logger.error(
                f"Meeting {meeting_id} processing failed: {error_message}"
            )
        
        return success
    
    def retry_processing(self, meeting_id: int) -> bool:
        """Retry processing for a failed meeting.
        
        Transitions from FAILED back to AUDIO_UPLOADED.
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            True if retry was initiated
        """
        return self.meeting_service.transition_status(
            meeting_id, ProcessingStatus.AUDIO_UPLOADED
        )
    
    def get_processing_status(self, meeting_id: int) -> dict:
        """Get detailed processing status for a meeting.
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Dictionary with processing details
        """
        meeting = self.meeting_service.get_by_id(meeting_id)
        
        if not meeting:
            return {"error": "Meeting not found"}
        
        jobs = job_service.get_jobs_by_meeting(meeting_id)
        
        return {
            "meeting_id": meeting.id,
            "title": meeting.title,
            "current_status": meeting.status,
            "is_terminal": ProcessingStatus(meeting.status) in ProcessingStatus.terminal_states(),
            "is_active": ProcessingStatus(meeting.status) in ProcessingStatus.active_states(),
            "is_processing": ProcessingStatus(meeting.status) in ProcessingStatus.processing_states(),
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
        """Mark meeting as having audio uploaded.
        
        Transitions from CREATED or RECORDING to AUDIO_UPLOADED.
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            True if transition was successful
        """
        return self.meeting_service.transition_status(
            meeting_id, ProcessingStatus.AUDIO_UPLOADED
        )
    
    def mark_recording(self, meeting_id: int) -> bool:
        """Mark meeting as currently recording.
        
        Transitions from CREATED to RECORDING.
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            True if transition was successful
        """
        return self.meeting_service.transition_status(
            meeting_id, ProcessingStatus.RECORDING
        )
