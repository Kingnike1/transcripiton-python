"""Local pyannote speaker-diarization provider."""

from collections.abc import Callable
from typing import Any, Optional
from uuid import uuid4

from app.core.time import utc_now
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
    ) -> None:
        if pipeline_factory is None:
            try:
                from pyannote.audio import Pipeline
            except ImportError as exc:  # pragma: no cover - environment contract
                raise RuntimeError(
                    "pyannote.audio is not installed; install requirements-worker.txt"
                ) from exc
            pipeline_factory = Pipeline.from_pretrained

        kwargs: dict[str, Any] = {}
        if token:
            kwargs["token"] = token
        self.pipeline = pipeline_factory(model_name, **kwargs)
        self.device = device
        if device != "cpu":  # pragma: no cover - depends on optional torch runtime
            try:
                import torch

                self.pipeline.to(torch.device(device))
            except ImportError as exc:
                raise RuntimeError("torch is required for non-CPU diarization") from exc

    def diarize(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
    ) -> DiarizationResult:
        kwargs: dict[str, Any] = {}
        if num_speakers is not None:
            kwargs["num_speakers"] = num_speakers
        output = self.pipeline(audio_path, **kwargs)
        annotation = getattr(output, "exclusive_speaker_diarization", None)
        if annotation is None:
            annotation = getattr(output, "speaker_diarization", output)

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
