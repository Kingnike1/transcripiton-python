"""Tests for ffprobe-backed audio inspection."""

from pathlib import Path
import subprocess

import pytest

from app.exceptions.audio import AudioFormatError, AudioInspectorUnavailableError
from app.services.audio_inspector import FFprobeAudioInspector


def test_ffprobe_metadata_is_normalized(monkeypatch, tmp_path):
    media_path = tmp_path / "meeting.wav"
    media_path.write_bytes(b"placeholder")

    monkeypatch.setattr("app.services.audio_inspector.shutil.which", lambda _binary: "/usr/bin/ffprobe")

    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"streams":[{"codec_type":"audio","codec_name":"pcm_s16le","channels":2,"sample_rate":"48000"}],"format":{"duration":"8.25"}}',
            stderr="",
        )

    monkeypatch.setattr("app.services.audio_inspector.subprocess.run", fake_run)

    metadata = FFprobeAudioInspector().inspect(media_path)

    assert metadata.duration_seconds == 8.25
    assert metadata.codec_name == "pcm_s16le"
    assert metadata.channels == 2
    assert metadata.sample_rate == 48000


def test_missing_ffprobe_is_reported_as_server_capability_error(monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.audio_inspector.shutil.which", lambda _binary: None)

    with pytest.raises(AudioInspectorUnavailableError):
        FFprobeAudioInspector().inspect(tmp_path / "meeting.wav")


def test_media_without_audio_stream_is_rejected(monkeypatch, tmp_path):
    media_path = tmp_path / "meeting.webm"
    media_path.write_bytes(b"placeholder")
    monkeypatch.setattr("app.services.audio_inspector.shutil.which", lambda _binary: "/usr/bin/ffprobe")

    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"streams":[{"codec_type":"video","codec_name":"vp9"}],"format":{}}',
            stderr="",
        )

    monkeypatch.setattr("app.services.audio_inspector.subprocess.run", fake_run)

    with pytest.raises(AudioFormatError, match="does not contain an audio stream"):
        FFprobeAudioInspector().inspect(media_path)
