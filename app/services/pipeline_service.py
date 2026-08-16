"""Orchestrate the current provider-based processing pipeline scaffold."""

import logging
from typing import Any, Optional

from app.services.interfaces import (
    IAISummarizer,
    IExporter,
    ISpeakerIdentifier,
    ITranscriber,
)

logger = logging.getLogger(__name__)


class PipelineService:
    """Coordinate registered pipeline providers without persisting results."""

    def __init__(self) -> None:
        self._transcriber: Optional[ITranscriber] = None
        self._speaker_identifier: Optional[ISpeakerIdentifier] = None
        self._summarizer: Optional[IAISummarizer] = None
        self._exporter: Optional[IExporter] = None

    def register_transcriber(self, transcriber: ITranscriber) -> None:
        self._transcriber = transcriber
        logger.info("Registered transcriber: %s", type(transcriber).__name__)

    def register_speaker_identifier(self, identifier: ISpeakerIdentifier) -> None:
        self._speaker_identifier = identifier
        logger.info("Registered speaker identifier: %s", type(identifier).__name__)

    def register_summarizer(self, summarizer: IAISummarizer) -> None:
        self._summarizer = summarizer
        logger.info("Registered summarizer: %s", type(summarizer).__name__)

    def register_exporter(self, exporter: IExporter) -> None:
        self._exporter = exporter
        logger.info("Registered exporter: %s", type(exporter).__name__)

    def can_process_transcription(self) -> bool:
        return self._transcriber is not None

    def can_process_diarization(self) -> bool:
        return self._speaker_identifier is not None

    def can_process_summarization(self) -> bool:
        return self._summarizer is not None

    def can_process_export(self) -> bool:
        return self._exporter is not None

    def get_pipeline_status(self) -> dict[str, Any]:
        """Return provider availability without claiming the pipeline is persistent."""
        return {
            "transcription": {
                "available": self.can_process_transcription(),
                "implementation": (
                    type(self._transcriber).__name__ if self._transcriber else None
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
                    type(self._summarizer).__name__ if self._summarizer else None
                ),
            },
            "export": {
                "available": self.can_process_export(),
                "implementation": type(self._exporter).__name__ if self._exporter else None,
            },
            "ready": all(
                [
                    self.can_process_transcription(),
                    self.can_process_diarization(),
                    self.can_process_summarization(),
                    self.can_process_export(),
                ]
            ),
        }

    def execute_transcription_step(
        self,
        audio_path: str,
        language: str = "auto",
    ) -> Optional[dict[str, Any]]:
        transcriber = self._transcriber
        if transcriber is None:
            logger.warning("Transcription not available")
            return None

        try:
            result = transcriber.transcribe(audio_path, language)
            return {
                "text": result.text,
                "language": result.language,
                "segments": [
                    {
                        "text": segment.text,
                        "start": segment.start_time,
                        "end": segment.end_time,
                        "speaker": segment.speaker_label,
                    }
                    for segment in (result.segments or [])
                ],
            }
        except Exception:
            logger.exception("Transcription step failed")
            raise

    def execute_diarization_step(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
    ) -> Optional[dict[str, Any]]:
        identifier = self._speaker_identifier
        if identifier is None:
            logger.warning("Diarization not available")
            return None

        try:
            result = identifier.diarize(audio_path, num_speakers)
            return {
                "segments": [
                    {
                        "start": segment.start_time,
                        "end": segment.end_time,
                        "speaker": segment.speaker_label,
                        "confidence": segment.confidence,
                    }
                    for segment in (result.segments or [])
                ],
                "num_speakers": result.num_speakers,
            }
        except Exception:
            logger.exception("Diarization step failed")
            raise

    def execute_summarization_step(
        self,
        transcript_text: str,
    ) -> Optional[dict[str, Any]]:
        summarizer = self._summarizer
        if summarizer is None:
            logger.warning("Summarization not available")
            return None

        try:
            result = summarizer.summarize(transcript_text)
            return {
                "summary": result.summary,
                "action_items": result.action_items or [],
                "decisions": result.decisions or [],
                "risks": result.risks or [],
                "open_questions": result.open_questions or [],
                "follow_up_tasks": result.follow_up_tasks or [],
            }
        except Exception:
            logger.exception("Summarization step failed")
            raise

    def execute_export_step(
        self,
        meeting_id: int,
        format: str = "markdown",
        analysis: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Execute export; ``analysis`` remains reserved for a future provider contract."""
        del analysis
        exporter = self._exporter
        if exporter is None:
            logger.warning("Export not available")
            return None

        try:
            result = exporter.export(meeting_id, format)
            return {
                "file_path": result.file_path,
                "format": result.format,
                "file_size_bytes": result.file_size_bytes,
            }
        except Exception:
            logger.exception("Export step failed")
            raise

    def process_full_pipeline(
        self,
        meeting_id: int,
        audio_path: str,
        language: str = "auto",
    ) -> dict[str, Any]:
        """Run the non-persistent prototype pipeline in sequence."""
        results: dict[str, Any] = {
            "meeting_id": meeting_id,
            "audio_path": audio_path,
            "steps": {},
        }

        logger.info("Starting full pipeline for meeting %s", meeting_id)
        transcription = self.execute_transcription_step(audio_path, language)
        results["steps"]["transcription"] = transcription
        if transcription is None:
            raise RuntimeError("Transcription step failed or not available")

        results["steps"]["diarization"] = self.execute_diarization_step(audio_path)
        results["steps"]["summarization"] = self.execute_summarization_step(
            str(transcription.get("text", ""))
        )

        logger.info("Full pipeline completed for meeting %s", meeting_id)
        return results


pipeline_service = PipelineService()
