"""Tests for the first real transcription vertical slice."""

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from sqlalchemy.orm import sessionmaker

from app.core.enums import JobStatus, JobType, ProcessingStatus
from app.models.audio import Audio
from app.models.meeting import Meeting
from app.providers.transcriber.faster_whisper import FasterWhisperTranscriber
from app.services.interfaces import ITranscriber, TranscriptResult, TranscriptSegment
from app.services.persistent_job_service import PersistentJobService
from app.services.transcription_service import TranscriptionService
from app.workers.job_worker import JobWorker
from app.workers.transcription_handler import TranscriptionJobHandler


@dataclass
class FakeTranscriber(ITranscriber):
    result: TranscriptResult
    calls: int = 0

    def transcribe(self, audio_path: str, language: str = "auto") -> TranscriptResult:
        self.calls += 1
        self.result.audio_path = audio_path
        return self.result

    def get_supported_languages(self) -> list[str]:
        return ["auto", "pt"]


def _meeting_audio(db_session, relative_path: str) -> tuple[Meeting, Audio]:
    meeting = Meeting(title="Transcribe", status=ProcessingStatus.AUDIO_UPLOADED.value)
    db_session.add(meeting)
    db_session.flush()
    audio = Audio(
        meeting_id=meeting.id,
        filename="sample.wav",
        file_path=relative_path,
        file_size=8,
        mime_type="audio/wav",
    )
    db_session.add(audio)
    db_session.commit()
    return meeting, audio


def _result() -> TranscriptResult:
    return TranscriptResult(
        id="provider-result",
        audio_path="",
        text="Olá mundo. Segunda frase.",
        language="pt",
        segments=[
            TranscriptSegment("Olá mundo.", 0.0, 1.2, confidence=0.9),
            TranscriptSegment("Segunda frase.", 1.2, 2.5, confidence=0.8),
        ],
    )


def test_faster_whisper_adapter_consumes_generator_and_maps_segments() -> None:
    captured = {}

    class FakeModel:
        def transcribe(self, path, **kwargs):
            captured["path"] = path
            captured["kwargs"] = kwargs
            segments = iter(
                [
                    SimpleNamespace(text=" Olá ", start=0.0, end=1.0, avg_logprob=-0.1),
                    SimpleNamespace(text=" mundo ", start=1.0, end=2.0, avg_logprob=-0.2),
                ]
            )
            return segments, SimpleNamespace(language="pt")

    def factory(model_name, **kwargs):
        captured["model_name"] = model_name
        captured["model_kwargs"] = kwargs
        return FakeModel()

    provider = FasterWhisperTranscriber(
        model_name="base",
        device="cpu",
        compute_type="int8",
        model_factory=factory,
    )
    result = provider.transcribe("meeting.wav", "auto")

    assert captured["model_name"] == "base"
    assert captured["model_kwargs"] == {"device": "cpu", "compute_type": "int8"}
    assert captured["kwargs"]["language"] is None
    assert result.text == "Olá mundo"
    assert result.language == "pt"
    assert len(result.segments or []) == 2
    assert result.segments[0].confidence is not None


def test_persist_result_saves_ordered_segments_and_transcribed_status(db_session) -> None:
    meeting, audio = _meeting_audio(db_session, "audio/sample.wav")
    meeting.status = ProcessingStatus.TRANSCRIBING.value
    db_session.commit()

    transcription = TranscriptionService(db_session).persist_result(
        meeting.id,
        audio.id,
        _result(),
    )

    assert transcription.text == "Olá mundo. Segunda frase."
    assert [segment.sequence for segment in transcription.segments] == [1, 2]
    assert [segment.text for segment in transcription.segments] == ["Olá mundo.", "Segunda frase."]
    db_session.expire_all()
    assert db_session.get(Meeting, meeting.id).status == ProcessingStatus.TRANSCRIBED.value


def test_transcription_handler_runs_provider_and_persists_result(db_session, tmp_path) -> None:
    storage = tmp_path / "storage"
    audio_dir = storage / "audio"
    audio_dir.mkdir(parents=True)
    (audio_dir / "sample.wav").write_bytes(b"RIFFfake")
    meeting, audio = _meeting_audio(db_session, "audio/sample.wav")
    job = PersistentJobService(db_session).create_job(
        meeting.id,
        JobType.TRANSCRIBE,
        {"audio_id": audio.id},
    )
    SessionFactory = sessionmaker(bind=db_session.get_bind())
    provider = FakeTranscriber(_result())
    handler = TranscriptionJobHandler(
        transcriber=provider,
        session_factory=SessionFactory,
        storage_path=str(storage),
        language="auto",
    )
    worker = JobWorker(
        handlers={JobType.TRANSCRIBE: handler},
        failure_handlers={JobType.TRANSCRIBE: handler.on_terminal_failure},
        session_factory=SessionFactory,
        worker_id="transcriber-test",
    )

    assert worker.run_once() is True

    db_session.expire_all()
    persisted_job = PersistentJobService(db_session).get_job(job.id)
    transcription = TranscriptionService(db_session).get_by_meeting(meeting.id)
    assert persisted_job is not None
    assert persisted_job.status == JobStatus.COMPLETED.value
    assert transcription is not None
    assert transcription.language == "pt"
    assert len(transcription.segments) == 2
    assert db_session.get(Meeting, meeting.id).status == ProcessingStatus.TRANSCRIBED.value
    assert provider.calls == 1


def test_transcription_handler_rejects_storage_escape(db_session, tmp_path) -> None:
    meeting, audio = _meeting_audio(db_session, "../outside.wav")
    job = PersistentJobService(db_session).create_job(
        meeting.id,
        JobType.TRANSCRIBE,
        {"audio_id": audio.id},
        max_attempts=1,
    )
    SessionFactory = sessionmaker(bind=db_session.get_bind())
    provider = FakeTranscriber(_result())
    handler = TranscriptionJobHandler(
        provider,
        session_factory=SessionFactory,
        storage_path=str(tmp_path / "storage"),
    )
    worker = JobWorker(
        handlers={JobType.TRANSCRIBE: handler},
        failure_handlers={JobType.TRANSCRIBE: handler.on_terminal_failure},
        session_factory=SessionFactory,
        worker_id="failure-test",
        retry_delay_seconds=0,
    )

    assert worker.run_once() is True
    db_session.expire_all()
    assert PersistentJobService(db_session).get_job(job.id).status == JobStatus.FAILED.value
    assert db_session.get(Meeting, meeting.id).status == ProcessingStatus.FAILED.value
    assert provider.calls == 0


def test_transcription_api_returns_segments(client, db_session) -> None:
    meeting, audio = _meeting_audio(db_session, "audio/sample.wav")
    meeting.status = ProcessingStatus.TRANSCRIBING.value
    db_session.commit()
    transcription = TranscriptionService(db_session).persist_result(meeting.id, audio.id, _result())

    response = client.get(f"/api/meetings/{meeting.id}/transcription")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == transcription.id
    assert payload["language"] == "pt"
    assert len(payload["segments"]) == 2
    assert payload["segments"][0]["start_time"] == 0.0
