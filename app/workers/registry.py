"""Worker composition root."""

from app.config import settings
from app.core.enums import JobType
from app.providers.speaker_identifier.pyannote import PyannoteSpeakerIdentifier
from app.providers.transcriber.faster_whisper import FasterWhisperTranscriber
from app.workers.diarization_handler import DiarizationJobHandler
from app.workers.job_worker import JobWorker
from app.workers.transcription_handler import TranscriptionJobHandler


def build_worker() -> JobWorker:
    """Build the background worker with transcription and diarization handlers."""
    transcriber = FasterWhisperTranscriber(
        model_name=settings.WHISPER_MODEL,
        device=settings.audio.WHISPER_DEVICE,
        compute_type=settings.audio.WHISPER_COMPUTE_TYPE,
        beam_size=settings.audio.WHISPER_BEAM_SIZE,
        vad_filter=settings.audio.WHISPER_VAD_FILTER,
    )
    transcription_handler = TranscriptionJobHandler(
        transcriber=transcriber,
        language=settings.WHISPER_LANGUAGE,
    )
    identifier = PyannoteSpeakerIdentifier(
        model_name=settings.PYANNOTE_MODEL,
        token=settings.ai.HUGGINGFACE_TOKEN,
        device=settings.PYANNOTE_DEVICE,
    )
    diarization_handler = DiarizationJobHandler(identifier=identifier)

    worker = JobWorker()
    worker.register_handler(
        JobType.TRANSCRIBE,
        transcription_handler,
        on_terminal_failure=transcription_handler.on_terminal_failure,
    )
    worker.register_handler(
        JobType.DIARIZE,
        diarization_handler,
        on_terminal_failure=diarization_handler.on_terminal_failure,
    )
    return worker
