"""Integration tests for audio HTTP endpoints."""

from app.api.dependencies import get_audio_service
from app.schemas.meeting import MeetingCreate
from app.services.audio_service import AudioService
from app.services.meeting_service import MeetingService
from app.services.storage_service import StorageService
from main import app


def wav_bytes() -> bytes:
    return b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * 32


def test_upload_and_get_audio_metadata(client, db_session, tmp_path):
    meeting = MeetingService(db_session).create(MeetingCreate(title="API audio meeting"))

    def override_audio_service():
        return AudioService(db_session, storage=StorageService(str(tmp_path)))

    app.dependency_overrides[get_audio_service] = override_audio_service
    response = client.post(
        f"/api/meetings/{meeting.id}/audio",
        files={"file": ("meeting.wav", wav_bytes(), "audio/wav")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "AUDIO_UPLOADED"
    assert body["audio"]["filename"] == "meeting.wav"

    metadata = client.get(f"/api/meetings/{meeting.id}/audio")
    assert metadata.status_code == 200
    assert metadata.json()["file_size"] == len(wav_bytes())


def test_upload_to_unknown_meeting_returns_404(client, db_session, tmp_path):
    def override_audio_service():
        return AudioService(db_session, storage=StorageService(str(tmp_path)))

    app.dependency_overrides[get_audio_service] = override_audio_service
    response = client.post(
        "/api/meetings/999/audio",
        files={"file": ("meeting.wav", wav_bytes(), "audio/wav")},
    )
    assert response.status_code == 404


def test_duplicate_upload_returns_409(client, db_session, tmp_path):
    meeting = MeetingService(db_session).create(MeetingCreate(title="Duplicate audio"))

    def override_audio_service():
        return AudioService(db_session, storage=StorageService(str(tmp_path)))

    app.dependency_overrides[get_audio_service] = override_audio_service
    files = {"file": ("meeting.wav", wav_bytes(), "audio/wav")}
    assert client.post(f"/api/meetings/{meeting.id}/audio", files=files).status_code == 201
    response = client.post(f"/api/meetings/{meeting.id}/audio", files=files)
    assert response.status_code == 409
