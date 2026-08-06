"""Tests for secure audio upload use cases."""

import pytest

from app.core.enums import ProcessingStatus
from app.exceptions.audio import AudioAlreadyExistsError, AudioFormatError, AudioUploadError
from app.models.audio import Audio
from app.schemas.meeting import MeetingCreate
from app.services.audio_service import AudioService
from app.services.audio_validator import AudioValidator
from app.services.meeting_service import MeetingService
from app.services.storage_service import StorageService


def wav_bytes() -> bytes:
    return b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * 32


def create_meeting(db_session):
    return MeetingService(db_session).create(MeetingCreate(title="Audio meeting"))


def test_upload_persists_metadata_and_changes_status(db_session, tmp_path):
    meeting = create_meeting(db_session)
    service = AudioService(db_session, storage=StorageService(str(tmp_path)))

    audio = service.upload(meeting.id, "meeting.wav", "audio/wav", wav_bytes())

    assert audio.file_size == len(wav_bytes())
    assert audio.mime_type == "audio/wav"
    assert (tmp_path / audio.file_path).exists()
    db_session.refresh(meeting)
    assert meeting.status == ProcessingStatus.AUDIO_UPLOADED.value


def test_duplicate_upload_is_rejected(db_session, tmp_path):
    meeting = create_meeting(db_session)
    service = AudioService(db_session, storage=StorageService(str(tmp_path)))
    service.upload(meeting.id, "meeting.wav", "audio/wav", wav_bytes())

    with pytest.raises(AudioAlreadyExistsError):
        service.upload(meeting.id, "second.wav", "audio/wav", wav_bytes())


def test_empty_file_is_rejected():
    with pytest.raises(AudioUploadError):
        AudioValidator().validate("meeting.wav", "audio/wav", b"")


def test_mime_mismatch_is_rejected():
    with pytest.raises(AudioFormatError):
        AudioValidator().validate("meeting.wav", "audio/mpeg", wav_bytes())


def test_fake_audio_content_is_rejected():
    with pytest.raises(AudioFormatError):
        AudioValidator().validate("meeting.wav", "audio/wav", b"not-a-wave-file")


def test_database_failure_removes_stored_file(db_session, tmp_path, monkeypatch):
    meeting = create_meeting(db_session)
    service = AudioService(db_session, storage=StorageService(str(tmp_path)))

    def fail_add(_audio):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(service.audios, "add", fail_add)
    with pytest.raises(RuntimeError):
        service.upload(meeting.id, "meeting.wav", "audio/wav", wav_bytes())

    assert list((tmp_path / "audio" / str(meeting.id)).glob("*")) == []


def test_commit_failure_rolls_back_database_and_removes_file(
    db_session, tmp_path, monkeypatch
):
    """A failed unit-of-work commit must rollback DB state and compensate storage."""
    meeting = create_meeting(db_session)
    service = AudioService(db_session, storage=StorageService(str(tmp_path)))

    def fail_commit() -> None:
        raise RuntimeError("commit unavailable")

    monkeypatch.setattr(service.uow, "commit", fail_commit)

    with pytest.raises(RuntimeError, match="commit unavailable"):
        service.upload(meeting.id, "meeting.wav", "audio/wav", wav_bytes())

    assert db_session.query(Audio).count() == 0
    db_session.refresh(meeting)
    assert meeting.status == ProcessingStatus.CREATED.value
    assert list((tmp_path / "audio" / str(meeting.id)).glob("*")) == []
