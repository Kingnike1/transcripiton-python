"""Integration tests for audio HTTP endpoints."""

from app.api.dependencies import get_audio_service
from app.schemas.meeting import MeetingCreate
from app.services.audio_service import AudioService
from app.services.meeting_service import MeetingService
from app.services.storage_service import StorageService
from main import app
from tests.audio_fakes import FakeAudioInspector


def wav_bytes(marker: bytes = b"") -> bytes:
    return b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + marker + b"\x00" * 32


def _service(db_session, tmp_path):
    return AudioService(
        db_session,
        storage=StorageService(str(tmp_path)),
        inspector=FakeAudioInspector(),
    )


def test_upload_and_get_audio_metadata(client, db_session, tmp_path):
    meeting = MeetingService(db_session).create(MeetingCreate(title="API audio meeting"))

    def override_audio_service():
        return _service(db_session, tmp_path)

    app.dependency_overrides[get_audio_service] = override_audio_service
    response = client.post(
        f"/api/meetings/{meeting.id}/audio",
        files={"file": ("meeting.wav", wav_bytes(), "audio/wav")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "AUDIO_UPLOADED"
    assert body["audio"]["filename"] == "meeting.wav"
    assert body["audio"]["duration"] == 13
    assert body["audio"]["codec_name"] == "pcm_s16le"
    assert body["audio"]["channels"] == 1
    assert body["audio"]["sample_rate"] == 16000
    assert "file_path" not in body["audio"]

    metadata = client.get(f"/api/meetings/{meeting.id}/audio")
    assert metadata.status_code == 200
    metadata_body = metadata.json()
    assert metadata_body["file_size"] == len(wav_bytes())
    assert "file_path" not in metadata_body


def test_upload_to_unknown_meeting_returns_404(client, db_session, tmp_path):
    def override_audio_service():
        return _service(db_session, tmp_path)

    app.dependency_overrides[get_audio_service] = override_audio_service
    response = client.post(
        "/api/meetings/999/audio",
        files={"file": ("meeting.wav", wav_bytes(), "audio/wav")},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_duplicate_upload_returns_409(client, db_session, tmp_path):
    meeting = MeetingService(db_session).create(MeetingCreate(title="Duplicate audio"))

    def override_audio_service():
        return _service(db_session, tmp_path)

    app.dependency_overrides[get_audio_service] = override_audio_service
    files = {"file": ("meeting.wav", wav_bytes(), "audio/wav")}
    assert client.post(f"/api/meetings/{meeting.id}/audio", files=files).status_code == 201
    response = client.post(f"/api/meetings/{meeting.id}/audio", files=files)
    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICT"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_upload_policy_exposes_safe_constraints(client, db_session, tmp_path):
    meeting = MeetingService(db_session).create(MeetingCreate(title="Upload policy"))

    def override_audio_service():
        return _service(db_session, tmp_path)

    app.dependency_overrides[get_audio_service] = override_audio_service
    response = client.get(f"/api/meetings/{meeting.id}/audio/policy")
    assert response.status_code == 200
    body = response.json()
    assert ".wav" in body["allowed_extensions"]
    assert body["max_size_bytes"] > 0
    assert body["has_audio"] is False
    assert body["can_replace"] is False
    assert "storage_path" not in response.text.lower()


def test_audio_can_be_replaced_before_processing(client, db_session, tmp_path):
    meeting = MeetingService(db_session).create(MeetingCreate(title="Replace audio"))

    def override_audio_service():
        return _service(db_session, tmp_path)

    app.dependency_overrides[get_audio_service] = override_audio_service
    first = client.post(
        f"/api/meetings/{meeting.id}/audio",
        files={"file": ("first.wav", wav_bytes(), "audio/wav")},
    )
    assert first.status_code == 201
    policy = client.get(f"/api/meetings/{meeting.id}/audio/policy").json()
    assert policy["can_replace"] is True

    replacement = client.post(
        f"/api/meetings/{meeting.id}/audio?replace=true",
        files={"file": ("second.wav", wav_bytes(b"X"), "audio/wav")},
    )
    assert replacement.status_code == 201
    assert replacement.json()["audio"]["filename"] == "second.wav"
    metadata = client.get(f"/api/meetings/{meeting.id}/audio")
    assert metadata.json()["filename"] == "second.wav"


def test_audio_replacement_is_blocked_after_processing_starts(client, db_session, tmp_path):
    meeting = MeetingService(db_session).create(MeetingCreate(title="Replace blocked"))

    def override_audio_service():
        return _service(db_session, tmp_path)

    app.dependency_overrides[get_audio_service] = override_audio_service
    assert client.post(
        f"/api/meetings/{meeting.id}/audio",
        files={"file": ("first.wav", wav_bytes(), "audio/wav")},
    ).status_code == 201
    assert client.post(f"/api/meetings/{meeting.id}/jobs/transcription").status_code == 201

    policy = client.get(f"/api/meetings/{meeting.id}/audio/policy").json()
    assert policy["can_replace"] is False
    replacement = client.post(
        f"/api/meetings/{meeting.id}/audio?replace=true",
        files={"file": ("second.wav", wav_bytes(b"Y"), "audio/wav")},
    )
    assert replacement.status_code == 400
    assert "antes do processamento" in replacement.json()["detail"].lower()


def test_invalid_extension_returns_unsupported_media_type(client, db_session, tmp_path):
    meeting = MeetingService(db_session).create(MeetingCreate(title="Invalid format"))

    def override_audio_service():
        return _service(db_session, tmp_path)

    app.dependency_overrides[get_audio_service] = override_audio_service
    response = client.post(
        f"/api/meetings/{meeting.id}/audio",
        files={"file": ("meeting.txt", b"not audio", "text/plain")},
    )
    assert response.status_code == 415
    assert response.json()["code"] == "UNSUPPORTED_MEDIA_TYPE"
