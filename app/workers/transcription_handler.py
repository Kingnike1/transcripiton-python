"""Worker handler for local speech-to-text jobs."""

from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.core.enums import ProcessingStatus
from app.database.session import SessionLocal
from app.models.processing_job import ProcessingJob
from app.services.interfaces import ITranscriber
from app.services.meeting_service import MeetingService
from app.services.transcription_service import TranscriptionService
from app.workers.job_worker import ProgressCallback, SessionFactory


class TranscriptionJobHandler:
    """Bridge a durable TRANSCRIBE job to a speech-to-text provider."""

    def __init__(
        self,
        transcriber: ITranscriber,
        session_factory: SessionFactory = SessionLocal,
        storage_path: str = settings.STORAGE_PATH,
        language: str = settings.WHISPER_LANGUAGE,
    ) -> None:
        self.transcriber = transcriber
        self.session_factory = session_factory
        self.storage_root = Path(storage_path).resolve()
        self.language = language

    def __call__(
        self,
        job: ProcessingJob,
        report_progress: ProgressCallback,
    ) -> dict[str, Any]:
        session = self.session_factory()
        try:
            audio_id = int(job.payload.get("audio_id", 0))
            audio = TranscriptionService(session).uow.audios.get_by_id(audio_id)
            if audio is None or audio.meeting_id != job.meeting_id:
                raise ValueError("Audio for transcription job was not found")

            transcription_service = TranscriptionService(session)
            existing = transcription_service.get_by_meeting(job.meeting_id)
            if existing is not None:
                return {"transcription_id": existing.id, "language": existing.language}

            meeting_service = MeetingService(session)
            meeting = meeting_service.get_by_id(job.meeting_id)
            if meeting is None:
                raise ValueError("Meeting not found")
            if meeting.status == ProcessingStatus.AUDIO_UPLOADED.value:
                if not meeting_service.transition_status(
                    job.meeting_id,
                    ProcessingStatus.TRANSCRIBING,
                ):
                    raise RuntimeError("Could not transition meeting to TRANSCRIBING")
            elif meeting.status != ProcessingStatus.TRANSCRIBING.value:
                raise ValueError(f"Meeting is not ready to transcribe: {meeting.status}")

            report_progress(5)
            audio_path = self._resolve_audio_path(audio.file_path)
            result = self.transcriber.transcribe(str(audio_path), self.language)
            report_progress(90)

            persisted = transcription_service.persist_result(
                meeting_id=job.meeting_id,
                audio_id=audio.id,
                result=result,
            )
            report_progress(95)
            return {
                "transcription_id": persisted.id,
                "language": persisted.language,
                "segments": len(persisted.segments),
            }
        finally:
            session.close()

    def on_terminal_failure(self, job: ProcessingJob, _error: str) -> None:
        """Only a terminal job failure should fail the meeting."""
        session: Session = self.session_factory()
        try:
            meeting = MeetingService(session).get_by_id(job.meeting_id)
            if meeting is None or meeting.status == ProcessingStatus.FAILED.value:
                return
            MeetingService(session).transition_status(
                job.meeting_id,
                ProcessingStatus.FAILED,
            )
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
