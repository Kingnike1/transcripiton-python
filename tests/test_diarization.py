"""Tests for the Sprint 10 speaker-diarization vertical slice."""

from types import SimpleNamespace

import pytest

from app.core.enums import ProcessingStatus
from app.models.audio import Audio
from app.models.meeting import Meeting
from app.providers.speaker_identifier.pyannote import PyannoteSpeakerIdentifier
from app.services.diarization_service import DiarizationService
from app.services.interfaces import DiarizationResult, SpeakerSegment, TranscriptResult, TranscriptSegment
from app.services.transcription_service import TranscriptionService


def _transcribed_meeting(db_session):
    meeting = Meeting(title="Diarization", status=ProcessingStatus.TRANSCRIBING.value)
    db_session.add(meeting)
    db_session.flush()
    audio = Audio(
        meeting_id=meeting.id,
        filename="sample.wav",
        file_path="audio/sample.wav",
        file_size=8,
        mime_type="audio/wav",
    )
    db_session.add(audio)
    db_session.commit()
    result = TranscriptResult(
        id="transcript",
        audio_path="audio/sample.wav",
        text="Olá mundo Segunda frase",
        language="pt",
        segments=[
            TranscriptSegment("Olá mundo", 0.0, 1.0),
            TranscriptSegment("Segunda frase", 1.0, 2.0),
        ],
    )
    transcription = TranscriptionService(db_session).persist_result(meeting.id, audio.id, result)
    return meeting, transcription


def test_pyannote_adapter_maps_exclusive_diarization():
    captured = {}

    class Turn:
        def __init__(self, start, end):
            self.start = start
            self.end = end

    class FakePipeline:
        def __call__(self, path, **kwargs):
            captured["path"] = path
            captured["kwargs"] = kwargs
            return SimpleNamespace(
                exclusive_speaker_diarization=[
                    (Turn(0.0, 1.1), "SPEAKER_00"),
                    (Turn(1.1, 2.2), "SPEAKER_01"),
                ]
            )

    def factory(model_name, **kwargs):
        captured["model"] = model_name
        captured["factory_kwargs"] = kwargs
        return FakePipeline()

    provider = PyannoteSpeakerIdentifier(
        token="token",
        pipeline_factory=factory,
    )
    result = provider.diarize("meeting.wav", num_speakers=2)

    assert captured["model"] == "pyannote/speaker-diarization-community-1"
    assert captured["factory_kwargs"] == {"token": "token"}
    assert captured["kwargs"] == {"num_speakers": 2}
    assert result.num_speakers == 2
    assert [segment.speaker_label for segment in result.segments or []] == [
        "SPEAKER_00",
        "SPEAKER_01",
    ]


def test_pyannote_adapter_rejects_missing_pipeline():
    def factory(_model_name, **_kwargs):
        return None

    with pytest.raises(RuntimeError, match="pipeline could not be loaded"):
        PyannoteSpeakerIdentifier(token="token", pipeline_factory=factory)


def test_pyannote_adapter_rejects_result_without_annotation():
    class FakePipeline:
        def __call__(self, _path, **_kwargs):
            return SimpleNamespace()

    provider = PyannoteSpeakerIdentifier(
        token="token",
        pipeline_factory=lambda _model_name, **_kwargs: FakePipeline(),
    )

    with pytest.raises(RuntimeError, match="does not contain a diarization annotation"):
        provider.diarize("meeting.wav")


def test_diarization_persists_speakers_and_reconciles_text(db_session):
    meeting, transcription = _transcribed_meeting(db_session)
    meeting.status = ProcessingStatus.DIARIZING.value
    db_session.commit()

    result = DiarizationResult(
        id="diarization",
        audio_path="audio/sample.wav",
        num_speakers=2,
        segments=[
            SpeakerSegment(0.0, 0.9, "SPEAKER_00"),
            SpeakerSegment(0.9, 2.1, "SPEAKER_01"),
        ],
    )
    rows = DiarizationService(db_session).persist_result(meeting.id, transcription, result)

    assert len(rows) == 2
    assert rows[0].speaker_label == "SPEAKER_00"
    assert rows[0].text == "Olá mundo"
    assert "Segunda frase" in rows[1].text
    db_session.expire_all()
    assert db_session.get(Meeting, meeting.id).status == ProcessingStatus.DIARIZED.value


def test_diarization_api_returns_persisted_segments(client, db_session):
    meeting, transcription = _transcribed_meeting(db_session)
    meeting.status = ProcessingStatus.DIARIZING.value
    db_session.commit()
    DiarizationService(db_session).persist_result(
        meeting.id,
        transcription,
        DiarizationResult(
            id="result",
            audio_path="audio/sample.wav",
            num_speakers=1,
            segments=[SpeakerSegment(0.0, 2.0, "SPEAKER_00")],
        ),
    )

    response = client.get(f"/api/meetings/{meeting.id}/diarization")
    assert response.status_code == 200
    payload = response.json()
    assert payload["num_speakers"] == 1
    assert payload["segments"][0]["speaker_label"] == "SPEAKER_00"
