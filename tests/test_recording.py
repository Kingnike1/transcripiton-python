"""Tests for Stack 17 browser microphone recording integration."""

from app.schemas.meeting import MeetingCreate
from app.services.audio_service import AudioService
from app.services.audio_validator import AudioValidator
from app.services.meeting_service import MeetingService
from app.services.storage_service import StorageService
from tests.audio_fakes import FakeAudioInspector


def webm_bytes() -> bytes:
    return b"\x1a\x45\xdf\xa3" + b"\x00" * 64


def test_validator_accepts_media_recorder_codec_parameters():
    validator = AudioValidator()

    validator.validate(
        "recording.webm",
        "audio/webm;codecs=opus",
        webm_bytes(),
    )


def test_audio_service_persists_normalized_browser_mime(db_session, tmp_path):
    meeting = MeetingService(db_session).create(MeetingCreate(title="Browser recording"))
    service = AudioService(
        db_session,
        storage=StorageService(str(tmp_path)),
        validator=AudioValidator(),
        inspector=FakeAudioInspector(),
    )

    audio = service.upload(
        meeting.id,
        "recording.webm",
        "audio/webm;codecs=opus",
        webm_bytes(),
    )

    assert audio.mime_type == "audio/webm"


def test_meeting_page_exposes_microphone_recording_controls(client):
    created = client.post(
        "/api/meetings",
        json={"title": "Recorded meeting", "description": "Microphone test"},
    )
    assert created.status_code == 201
    meeting_id = created.json()["id"]

    page = client.get(f"/meetings/{meeting_id}")

    assert page.status_code == 200
    assert 'id="recordStartBtn"' in page.text
    assert 'id="recordPreview"' in page.text
    assert "/static/js/meeting_recording.js" in page.text


def test_recording_controller_is_served(client):
    response = client.get("/static/js/meeting_recording.js")

    assert response.status_code == 200
    assert "navigator.mediaDevices.getUserMedia" in response.text
    assert "MediaRecorder" in response.text
    assert "window.isSecureContext" in response.text
