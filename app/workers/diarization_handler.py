"""Worker handler for speaker diarization jobs."""

from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.core.enums import ProcessingStatus
from app.database.session import SessionLocal
from app.models.processing_job import ProcessingJob
from app.services.diarization_service import DiarizationService
from app.services.interfaces import ISpeakerIdentifier
from app.services.meeting_service import MeetingService
from app.services.transcription_service import TranscriptionService
from app.workers.job_worker import ProgressCallback, SessionFactory


class DiarizationJobHandler:
    """Bridge a durable DIARIZE job to a speaker provider."""

    def __init__(
        self,
        identifier: ISpeakerIdentifier,
        session_factory: SessionFactory = SessionLocal,
        storage_path: str = settings.STORAGE_PATH,
    ) -> None:
        self.identifier = identifier
        self.session_factory = session_factory
        self.storage_root = Path(storage_path).resolve()

    def __call__(self, job: ProcessingJob, report_progress: ProgressCallback) -> dict[str, Any]:
        session = self.session_factory()
        try:
            transcription = TranscriptionService(session).get_by_meeting(job.meeting_id)
            if transcription is None:
                raise ValueError("Meeting has no persisted transcription")
            existing = DiarizationService(session).get_by_meeting(job.meeting_id)
            if existing:
                labels = {segment.speaker_label for segment in existing}
                return {"segments": len(existing), "num_speakers": len(labels)}

            meeting_service = MeetingService(session)
            meeting = meeting_service.get_by_id(job.meeting_id)
            if meeting is None:
                raise ValueError("Meeting not found")
            if meeting.status == ProcessingStatus.TRANSCRIBED.value:
                if not meeting_service.transition_status(job.meeting_id, ProcessingStatus.DIARIZING):
                    raise RuntimeError("Could not transition meeting to DIARIZING")
            elif meeting.status != ProcessingStatus.DIARIZING.value:
                raise ValueError(f"Meeting is not ready to diarize: {meeting.status}")

            audio = transcription.audio
            report_progress(5)
            result = self.identifier.diarize(
                str(self._resolve_audio_path(audio.file_path)),
                job.payload.get("num_speakers"),
            )
            report_progress(90)
            rows = DiarizationService(session).persist_result(job.meeting_id, transcription, result)
            report_progress(95)
            return {"segments": len(rows), "num_speakers": result.num_speakers}
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

    def _resolve_audio_path(self, relative_path: str) -> Path:
        candidate = (self.storage_root / relative_path).resolve()
        try:
            candidate.relative_to(self.storage_root)
        except ValueError as exc:
            raise ValueError("Audio path escapes configured storage") from exc
        if not candidate.is_file():
            raise FileNotFoundError("Stored audio file is missing")
        return candidate
