"""Local pyannote speaker-diarization provider."""

from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
import os
import subprocess
import tempfile
from typing import Any, Iterator, Optional
from uuid import uuid4

from app.core.time import utc_now
from app.infrastructure.media_runtime import prepare_media_runtime
from app.services.interfaces import DiarizationResult, ISpeakerIdentifier, SpeakerSegment

PipelineFactory = Callable[..., Any]


class PyannoteSpeakerIdentifier(ISpeakerIdentifier):
    """Run local speaker diarization through pyannote.audio."""

    def __init__(
        self,
        model_name: str = "pyannote/speaker-diarization-community-1",
        token: Optional[str] = None,
        device: str = "cpu",
        pipeline_factory: Optional[PipelineFactory] = None,
        ffmpeg_bin_dir: Optional[str] = None,
    ) -> None:
        self._normalize_audio = pipeline_factory is None
        self._ffmpeg_bin_dir: Optional[Path] = None

        if pipeline_factory is None:
            try:
                self._ffmpeg_bin_dir = prepare_media_runtime(ffmpeg_bin_dir)
                from pyannote.audio import Pipeline
            except (ImportError, OSError, RuntimeError) as exc:  # pragma: no cover - environment contract
                raise RuntimeError(
                    "pyannote runtime is unavailable; verify requirements-worker.txt and the "
                    "FFmpeg Shared runtime on Windows (or FFmpeg libraries on Linux)"
                ) from exc
            pipeline_factory = Pipeline.from_pretrained

        kwargs: dict[str, Any] = {}
        if token:
            kwargs["token"] = token
        pipeline = pipeline_factory(model_name, **kwargs)
        if pipeline is None:
            raise RuntimeError(
                "pyannote pipeline could not be loaded; verify model access and HUGGINGFACE_TOKEN"
            )
        self.pipeline: Any = pipeline
        self.device = device
        if device != "cpu":  # pragma: no cover - depends on optional torch runtime
            try:
                import torch

                self.pipeline.to(torch.device(device))
            except ImportError as exc:
                raise RuntimeError("torch is required for non-CPU diarization") from exc

    @contextmanager
    def _prepared_audio(self, audio_path: str) -> Iterator[str]:
        """Yield normalized WAV/PCM audio with deterministic metadata for pyannote."""
        if not self._normalize_audio:
            yield audio_path
            return

        source = Path(audio_path)
        if not source.is_file():
            raise RuntimeError(f"audio file does not exist: {audio_path}")

        if self._ffmpeg_bin_dir is None:
            raise RuntimeError("FFmpeg runtime was not prepared for diarization")
        ffmpeg_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        ffmpeg_binary = self._ffmpeg_bin_dir / ffmpeg_name
        if not ffmpeg_binary.is_file():
            raise RuntimeError(f"FFmpeg executable was not found: {ffmpeg_binary}")

        with tempfile.TemporaryDirectory(prefix="amip-diarization-") as temp_dir:
            normalized = Path(temp_dir) / "normalized.wav"
            completed = subprocess.run(
                [
                    str(ffmpeg_binary),
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-i",
                    str(source),
                    "-vn",
                    "-ac",
                    "1",
                    "-ar",
                    "16000",
                    "-c:a",
                    "pcm_s16le",
                    str(normalized),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0 or not normalized.is_file():
                detail = completed.stderr.strip() or "unknown FFmpeg error"
                raise RuntimeError(f"failed to normalize audio for diarization: {detail}")

            yield str(normalized)

    def diarize(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
    ) -> DiarizationResult:
        kwargs: dict[str, Any] = {}
        if num_speakers is not None:
            kwargs["num_speakers"] = num_speakers

        with self._prepared_audio(audio_path) as prepared_audio_path:
            output = self.pipeline(prepared_audio_path, **kwargs)
        if output is None:
            raise RuntimeError("pyannote returned no diarization result")

        annotation = getattr(output, "exclusive_speaker_diarization", None)
        if annotation is None:
            annotation = getattr(output, "speaker_diarization", None)
        if annotation is None:
            raise RuntimeError("pyannote result does not contain a diarization annotation")

        segments: list[SpeakerSegment] = []
        labels: set[str] = set()
        for turn, speaker in annotation:
            label = str(speaker)
            labels.add(label)
            segments.append(
                SpeakerSegment(
                    start_time=float(turn.start),
                    end_time=float(turn.end),
                    speaker_label=label,
                )
            )
        return DiarizationResult(
            id=str(uuid4()),
            audio_path=audio_path,
            segments=segments,
            num_speakers=len(labels),
            created_at=utc_now(),
        )

    def diarize_async(self, audio_path: str, num_speakers: Optional[int] = None) -> str:
        raise NotImplementedError("Asynchrony belongs to the durable AMIP worker")

    def get_diarization_status(self, job_id: str) -> dict[str, Any]:
        raise NotImplementedError("Job status belongs to PersistentJobService")

    def count_speakers(self, audio_path: str) -> int:
        return self.diarize(audio_path).num_speakers or 0
