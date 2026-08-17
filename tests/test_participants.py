"""Tests for Stack 11 participant identity mapping."""

from app.core.enums import ProcessingStatus
from app.models.audio import Audio
from app.models.meeting import Meeting
from app.services.diarization_service import DiarizationService
from app.services.interfaces import DiarizationResult, SpeakerSegment, TranscriptResult, TranscriptSegment
from app.services.participant_service import ParticipantService
from app.services.transcription_service import TranscriptionService


def _diarized_meeting(db_session):
    meeting = Meeting(title="Participants", status=ProcessingStatus.TRANSCRIBING.value)
    db_session.add(meeting)
    db_session.flush()
    audio = Audio(
        meeting_id=meeting.id,
        filename="participants.wav",
        file_path="audio/participants.wav",
        file_size=16,
        mime_type="audio/wav",
    )
    db_session.add(audio)
    db_session.commit()

    transcription = TranscriptionService(db_session).persist_result(
        meeting.id,
        audio.id,
        TranscriptResult(
            id="transcript",
            audio_path="audio/participants.wav",
            text="Olá mundo Resposta final",
            language="pt",
            segments=[
                TranscriptSegment("Olá mundo", 0.0, 1.0),
                TranscriptSegment("Resposta final", 1.0, 2.0),
            ],
        ),
    )
    meeting.status = ProcessingStatus.DIARIZING.value
    db_session.commit()
    DiarizationService(db_session).persist_result(
        meeting.id,
        transcription,
        DiarizationResult(
            id="diarization",
            audio_path="audio/participants.wav",
            num_speakers=2,
            segments=[
                SpeakerSegment(0.0, 1.0, "SPEAKER_00"),
                SpeakerSegment(1.0, 2.0, "SPEAKER_01"),
            ],
        ),
    )
    return meeting


def test_diarization_creates_participant_placeholders(db_session):
    meeting = _diarized_meeting(db_session)

    participants = ParticipantService(db_session).list_by_meeting(meeting.id)

    assert [row.speaker_label for row in participants] == ["SPEAKER_00", "SPEAKER_01"]
    assert all(row.display_name is None for row in participants)
    assert all(row.confirmed is False for row in participants)


def test_participant_api_updates_and_persists_identity(client, db_session):
    meeting = _diarized_meeting(db_session)

    response = client.patch(
        f"/api/meetings/{meeting.id}/participants/SPEAKER_00",
        json={"display_name": "  Pablo  ", "confirmed": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["display_name"] == "Pablo"
    assert payload["confirmed"] is True

    listing = client.get(f"/api/meetings/{meeting.id}/participants")
    assert listing.status_code == 200
    participants = listing.json()["participants"]
    assert participants[0]["display_name"] == "Pablo"

    diarization = client.get(f"/api/meetings/{meeting.id}/diarization")
    assert diarization.status_code == 200
    diarization_payload = diarization.json()
    assert diarization_payload["participants"][0]["display_name"] == "Pablo"
    assert diarization_payload["segments"][0]["participant_name"] == "Pablo"
    assert diarization_payload["segments"][0]["participant_confirmed"] is True


def test_confirmed_participant_requires_name(client, db_session):
    meeting = _diarized_meeting(db_session)

    response = client.patch(
        f"/api/meetings/{meeting.id}/participants/SPEAKER_00",
        json={"display_name": "", "confirmed": True},
    )

    assert response.status_code == 422


def test_unknown_participant_returns_404(client, db_session):
    meeting = _diarized_meeting(db_session)

    response = client.patch(
        f"/api/meetings/{meeting.id}/participants/SPEAKER_99",
        json={"display_name": "Pessoa", "confirmed": True},
    )

    assert response.status_code == 404
