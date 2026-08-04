"""
Pipeline orchestration service.
Coordinates the full meeting processing pipeline.

This module defines the orchestration logic that connects
all pipeline components (transcription, diarization, summarization).
Actual implementations are injected via interfaces.
"""

import logging
from typing import Optional, Dict, Any

from app.core.enums import ProcessingStatus, JobType
from app.services.interfaces import (
    ITranscriber,
    ISpeakerIdentifier,
    IAISummarizer,
    IExporter,
    AIAnalysisResult,
)
from app.services.job_service import job_service, Job

logger = logging.getLogger(__name__)


class PipelineService:
    """Service for orchestrating the meeting processing pipeline.
    
    Coordinates the flow:
        Audio -> Transcription -> Diarization -> AI Analysis -> Export
    
    Each step is executed through its respective interface,
    allowing different implementations to be swapped in.
    
    Example:
        >>> pipeline = PipelineService()
        >>> pipeline.register_transcriber(WhisperTranscriber())
        >>> pipeline.register_speaker_identifier(PyannoteSpeakerIdentifier())
        >>> pipeline.register_summarizer(GPTSummarizer())
        >>> pipeline.register_exporter(MultiFormatExporter())
        >>> pipeline.process_full(meeting_id=1, audio_path="audio/meeting.mp3")
    """
    
    def __init__(self):
        """Initialize pipeline service with optional components."""
        self._transcriber: Optional[ITranscriber] = None
        self._speaker_identifier: Optional[ISpeakerIdentifier] = None
        self._summarizer: Optional[IAISummarizer] = None
        self._exporter: Optional[IExporter] = None
    
    def register_transcriber(self, transcriber: ITranscriber) -> None:
        """Register a transcription implementation.
        
        Args:
            transcriber: Implementation of ITranscriber
        """
        self._transcriber = transcriber
        logger.info("Registered transcriber: %s", type(transcriber).__name__)
    
    def register_speaker_identifier(self, identifier: ISpeakerIdentifier) -> None:
        """Register a speaker identification implementation.
        
        Args:
            identifier: Implementation of ISpeakerIdentifier
        """
        self._speaker_identifier = identifier
        logger.info(
            "Registered speaker identifier: %s", type(identifier).__name__
        )
    
    def register_summarizer(self, summarizer: IAISummarizer) -> None:
        """Register an AI summarization implementation.
        
        Args:
            summarizer: Implementation of IAISummarizer
        """
        self._summarizer = summarizer
        logger.info("Registered summarizer: %s", type(summarizer).__name__)
    
    def register_exporter(self, exporter: IExporter) -> None:
        """Register an export implementation.
        
        Args:
            exporter: Implementation of IExporter
        """
        self._exporter = exporter
        logger.info("Registered exporter: %s", type(exporter).__name__)
    
    def can_process_transcription(self) -> bool:
        """Check if transcription is available.
        
        Returns:
            True if transcriber is registered
        """
        return self._transcriber is not None
    
    def can_process_diarization(self) -> bool:
        """Check if speaker diarization is available.
        
        Returns:
            True if speaker identifier is registered
        """
        return self._speaker_identifier is not None
    
    def can_process_summarization(self) -> bool:
        """Check if AI summarization is available.
        
        Returns:
            True if summarizer is registered
        """
        return self._summarizer is not None
    
    def can_process_export(self) -> bool:
        """Check if export is available.
        
        Returns:
            True if exporter is registered
        """
        return self._exporter is not None
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline configuration status.
        
        Returns:
            Dictionary with component availability status
        """
        return {
            "transcription": {
                "available": self.can_process_transcription(),
                "implementation": (
                    type(self._transcriber).__name__
                    if self._transcriber
                    else None
                ),
            },
            "diarization": {
                "available": self.can_process_diarization(),
                "implementation": (
                    type(self._speaker_identifier).__name__
                    if self._speaker_identifier
                    else None
                ),
            },
            "summarization": {
                "available": self.can_process_summarization(),
                "implementation": (
                    type(self._summarizer).__name__
                    if self._summarizer
                    else None
                ),
            },
            "export": {
                "available": self.can_process_export(),
                "implementation": (
                    type(self._exporter).__name__
                    if self._exporter
                    else None
                ),
            },
            "ready": all([
                self.can_process_transcription(),
                self.can_process_diarization(),
                self.can_process_summarization(),
                self.can_process_export(),
            ]),
        }
    
    def execute_transcription_step(
        self, audio_path: str, language: str = "auto"
    ) -> Optional[Dict[str, Any]]:
        """Execute the transcription pipeline step.
        
        Args:
            audio_path: Path to audio file
            language: Language code
            
        Returns:
            Transcription result dict, or None if not available
        """
        if not self.can_process_transcription():
            logger.warning("Transcription not available")
            return None
        
        try:
            result = self._transcriber.transcribe(audio_path, language)
            return {
                "text": result.text,
                "language": result.language,
                "segments": [
                    {
                        "text": seg.text,
                        "start": seg.start_time,
                        "end": seg.end_time,
                        "speaker": seg.speaker_label,
                    }
                    for seg in (result.segments or [])
                ],
            }
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def execute_diarization_step(
        self, audio_path: str, num_speakers: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute the speaker diarization pipeline step.
        
        Args:
            audio_path: Path to audio file
            num_speakers: Expected number of speakers
            
        Returns:
            Diarization result dict, or None if not available
        """
        if not self.can_process_diarization():
            logger.warning("Diarization not available")
            return None
        
        try:
            result = self._speaker_identifier.diarize(audio_path, num_speakers)
            return {
                "segments": [
                    {
                        "start": seg.start_time,
                        "end": seg.end_time,
                        "speaker": seg.speaker_label,
                        "confidence": seg.confidence,
                    }
                    for seg in (result.segments or [])
                ],
                "num_speakers": result.num_speakers,
            }
        except Exception as e:
            logger.error(f"Diarization failed: {e}")
            raise
    
    def execute_summarization_step(
        self, transcript_text: str
    ) -> Optional[Dict[str, Any]]:
        """Execute the AI summarization pipeline step.
        
        Args:
            transcript_text: Full transcript text
            
        Returns:
            Analysis result dict, or None if not available
        """
        if not self.can_process_summarization():
            logger.warning("Summarization not available")
            return None
        
        try:
            result = self._summarizer.summarize(transcript_text)
            return {
                "summary": result.summary,
                "action_items": result.action_items or [],
                "decisions": result.decisions or [],
                "risks": result.risks or [],
                "open_questions": result.open_questions or [],
                "follow_up_tasks": result.follow_up_tasks or [],
            }
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise
    
    def execute_export_step(
        self,
        meeting_id: int,
        format: str = "markdown",
        analysis: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Execute the export pipeline step.
        
        Args:
            meeting_id: Meeting ID to export
            format: Export format
            analysis: Optional analysis data
            
        Returns:
            Export result dict, or None if not available
        """
        if not self.can_process_export():
            logger.warning("Export not available")
            return None
        
        try:
            result = self._exporter.export(meeting_id, format)
            return {
                "file_path": result.file_path,
                "format": result.format,
                "file_size_bytes": result.file_size_bytes,
            }
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise
    
    def process_full_pipeline(
        self, meeting_id: int, audio_path: str, language: str = "auto"
    ) -> Dict[str, Any]:
        """Process the full meeting pipeline.
        
        Executes all steps in sequence: transcription -> diarization
        -> summarization. Returns combined results.
        
        Args:
            meeting_id: Meeting ID
            audio_path: Path to audio file
            language: Language code
            
        Returns:
            Dictionary with results from all pipeline steps
            
        Raises:
            RuntimeError: If any pipeline step fails
        """
        results = {
            "meeting_id": meeting_id,
            "audio_path": audio_path,
            "steps": {},
        }
        
        # Step 1: Transcription
        logger.info(
            f"Starting full pipeline for meeting {meeting_id}"
        )
        transcription = self.execute_transcription_step(audio_path, language)
        results["steps"]["transcription"] = transcription
        
        if transcription is None:
            raise RuntimeError("Transcription step failed or not available")
        
        # Step 2: Diarization
        diarization = self.execute_diarization_step(audio_path)
        results["steps"]["diarization"] = diarization
        
        # Step 3: Summarization
        summarization = self.execute_summarization_step(transcription.get("text", ""))
        results["steps"]["summarization"] = summarization
        
        logger.info(
            f"Full pipeline completed for meeting {meeting_id}"
        )
        return results


# Singleton instance
pipeline_service = PipelineService()
