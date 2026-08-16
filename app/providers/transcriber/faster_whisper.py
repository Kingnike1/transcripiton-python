"""Local faster-whisper speech-to-text provider."""

import math
from collections.abc import Callable
from typing import Any, Optional
from uuid import uuid4

from app.core.time import utc_now
from app.services.interfaces import ITranscriber, TranscriptResult, TranscriptSegment

ModelFactory = Callable[..., Any]


class FasterWhisperTranscriber(ITranscriber):
    """Run Whisper locally through CTranslate2/faster-whisper."""

    def __init__(
        self,
        model_name: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        beam_size: int = 5,
        vad_filter: bool = True,
        model_factory: Optional[ModelFactory] = None,
    ) -> None:
        if model_factory is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:  # pragma: no cover - environment contract
                raise RuntimeError(
                    "faster-whisper is not installed; install requirements-worker.txt"
                ) from exc
            model_factory = WhisperModel

        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        self._model = model_factory(
            model_name,
            device=device,
            compute_type=compute_type,
        )

    def transcribe(self, audio_path: str, language: str = "auto") -> TranscriptResult:
        language_arg = None if language in {"", "auto"} else language
        raw_segments, info = self._model.transcribe(
            audio_path,
            language=language_arg,
            beam_size=self.beam_size,
            vad_filter=self.vad_filter,
        )

        segments: list[TranscriptSegment] = []
        text_parts: list[str] = []
        for raw in raw_segments:
            text = str(raw.text).strip()
            if not text:
                continue
            avg_logprob = getattr(raw, "avg_logprob", None)
            confidence = None
            if avg_logprob is not None:
                confidence = max(0.0, min(1.0, math.exp(float(avg_logprob))))
            segments.append(
                TranscriptSegment(
                    text=text,
                    start_time=float(raw.start),
                    end_time=float(raw.end),
                    confidence=confidence,
                )
            )
            text_parts.append(text)

        return TranscriptResult(
            id=str(uuid4()),
            audio_path=audio_path,
            text=" ".join(text_parts).strip(),
            language=getattr(info, "language", None),
            segments=segments,
            created_at=utc_now(),
        )

    def get_supported_languages(self) -> list[str]:
        return ["auto", "pt", "en", "es", "fr", "de", "it"]
