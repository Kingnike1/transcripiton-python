"""Reusable test doubles for audio upload tests."""

from pathlib import Path

from app.services.audio_inspector import AudioMediaMetadata


class FakeAudioInspector:
    """Return deterministic metadata without requiring ffprobe in unit tests."""

    def __init__(
        self,
        duration_seconds: float = 12.4,
        codec_name: str = "pcm_s16le",
        channels: int = 1,
        sample_rate: int = 16000,
    ) -> None:
        self.metadata = AudioMediaMetadata(
            duration_seconds=duration_seconds,
            codec_name=codec_name,
            channels=channels,
            sample_rate=sample_rate,
        )
        self.inspected_paths: list[Path] = []

    def inspect(self, path: Path) -> AudioMediaMetadata:
        self.inspected_paths.append(path)
        return self.metadata
