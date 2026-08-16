"""Tests for secure audio upload use cases."""

from io import BytesIO
import sqlite3

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.enums import ProcessingStatus
from app.exceptions.audio import AudioAlreadyExistsError, AudioFormatError, AudioUploadError
from app.models.audio import Audio
from app.schemas.meeting import MeetingCreate
from app.services.audio_service import AudioService
from app.services.audio_upload_stager import AudioUploadStager
from app.services.audio_validator import AudioValidator
from app.services.meeting_service import MeetingService
from app.services.storage_service import StorageService
from tests.audio_fakes import FakeAudioInspector


def wav_bytes(payload_size: int = 32) -> bytes:
    return b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * payload_size


def create_meeting(db_session):
    return MeetingService(db_session).create(MeetingCreate(title="Audio meeting"))


def create_service(db_session, tmp_path, *, max_size=None, chunk_size=None):
    storage = StorageService(str(tmp_path))
    validator = AudioValidator(max_size=max_size) if max_size is not None else AudioValidator()
    stager = (
        AudioUploadStager(storage, chunk_size=chunk_size)
        if chunk_size is not None
        else AudioUploadStager(storage)
    )
    return AudioService(
        db_session,
        storage=storage,
        validator=validator,
        inspector=FakeAudioInspector(),
        stager=stager,
    )


def test_upload_persists_metadata_and_changes_status(db_session, tmp_path):
    meeting = create_meeting(db_session)
    service = create_service(db_session, tmp_path)

    audio = service.upload(meeting.id, "meeting.wav", "audio/wav", wav_bytes())

    assert audio.file_size == len(wav_bytes())
    assert audio.mime_type == "audio/wav"
    assert audio.duration == 13
    assert audio.codec_name == "pcm_s16le"
    assert audio.channels == 1
    assert audio.sample_rate == 16000
    assert (tmp_path / audio.file_path).exists()
    assert list((tmp_path / "temp").glob("*")) == []
    db_session.refresh(meeting)
    assert meeting.status == ProcessingStatus.AUDIO_UPLOADED.value


def test_upload_stream_reads_in_bounded_chunks(db_session, tmp_path):
    meeting = create_meeting(db_session)
    service = create_service(db_session, tmp_path, chunk_size=8)

    class TrackingStream(BytesIO):
        def __init__(self, value: bytes):
            super().__init__(value)
            self.read_sizes = []

        def read(self, size=-1):
            self.read_sizes.append(size)
            return super().read(size)

    stream = TrackingStream(wav_bytes(80))
    service.upload_stream(meeting.id, "meeting.wav", "audio/wav", stream)

    assert stream.read_sizes
    assert -1 not in stream.read_sizes
    assert max(stream.read_sizes) <= 8
    assert len(stream.read_sizes) > 2


def test_size_limit_stops_stream_and_cleans_temp(db_session, tmp_path):
    meeting = create_meeting(db_session)
    service = create_service(db_session, tmp_path, max_size=20, chunk_size=8)

    with pytest.raises(AudioUploadError, match="exceeds the maximum size"):
        service.upload_stream(
            meeting.id,
            "meeting.wav",
            "audio/wav",
            BytesIO(wav_bytes(80)),
        )

    assert list((tmp_path / "temp").glob("*")) == []
    assert list((tmp_path / "audio" / str(meeting.id)).glob("*")) == []


def test_duplicate_upload_is_rejected(db_session, tmp_path):
    meeting = create_meeting(db_session)
    service = create_service(db_session, tmp_path)
    service.upload(meeting.id, "meeting.wav", "audio/wav", wav_bytes())

    with pytest.raises(AudioAlreadyExistsError):
        service.upload(meeting.id, "second.wav", "audio/wav", wav_bytes())


def test_concurrent_unique_conflict_is_translated_and_file_is_compensated(
    db_session, tmp_path, monkeypatch
):
    """A database race must become the same domain conflict as the fast pre-check."""
    meeting = create_meeting(db_session)
    service = create_service(db_session, tmp_path)

    def fail_with_unique_conflict() -> None:
        original = sqlite3.IntegrityError("UNIQUE constraint failed: audios.meeting_id")
        raise IntegrityError("INSERT INTO audios ...", {}, original)

    monkeypatch.setattr(service.uow, "commit", fail_with_unique_conflict)

    with pytest.raises(AudioAlreadyExistsError):
        service.upload(meeting.id, "meeting.wav", "audio/wav", wav_bytes())

    assert db_session.query(Audio).count() == 0
    db_session.refresh(meeting)
    assert meeting.status == ProcessingStatus.CREATED.value
    assert list((tmp_path / "temp").glob("*")) == []
    assert list((tmp_path / "audio" / str(meeting.id)).glob("*")) == []


def test_unrelated_integrity_error_is_not_misclassified(db_session, tmp_path, monkeypatch):
    """Only the active-audio constraint should map to AudioAlreadyExistsError."""
    meeting = create_meeting(db_session)
    service = create_service(db_session, tmp_path)

    def fail_with_other_integrity_error() -> None:
        original = sqlite3.IntegrityError("FOREIGN KEY constraint failed")
        raise IntegrityError("INSERT INTO audios ...", {}, original)

    monkeypatch.setattr(service.uow, "commit", fail_with_other_integrity_error)

    with pytest.raises(IntegrityError):
        service.upload(meeting.id, "meeting.wav", "audio/wav", wav_bytes())

    assert list((tmp_path / "audio" / str(meeting.id)).glob("*")) == []


def test_empty_file_is_rejected():
    with pytest.raises(AudioUploadError):
        AudioValidator().validate("meeting.wav", "audio/wav", b"")


def test_mime_mismatch_is_rejected():
    with pytest.raises(AudioFormatError):
        AudioValidator().validate("meeting.wav", "audio/mpeg", wav_bytes())


def test_fake_audio_content_is_rejected():
    with pytest.raises(AudioFormatError):
        AudioValidator().validate("meeting.wav", "audio/wav", b"not-a-wave-file")


def test_windows_style_path_filename_is_rejected():
    with pytest.raises(AudioUploadError, match="Invalid audio filename"):
        AudioValidator().validate("..\\meeting.wav", "audio/wav", wav_bytes())


def test_database_failure_removes_stored_file(db_session, tmp_path, monkeypatch):
    meeting = create_meeting(db_session)
    service = create_service(db_session, tmp_path)

    def fail_add(_audio):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(service.audios, "add", fail_add)
    with pytest.raises(RuntimeError):
        service.upload(meeting.id, "meeting.wav", "audio/wav", wav_bytes())

    assert list((tmp_path / "temp").glob("*")) == []
    assert list((tmp_path / "audio" / str(meeting.id)).glob("*")) == []


def test_commit_failure_rolls_back_database_and_removes_file(
    db_session, tmp_path, monkeypatch
):
    """A failed unit-of-work commit must rollback DB state and compensate storage."""
    meeting = create_meeting(db_session)
    service = create_service(db_session, tmp_path)

    def fail_commit() -> None:
        raise RuntimeError("commit unavailable")

    monkeypatch.setattr(service.uow, "commit", fail_commit)

    with pytest.raises(RuntimeError, match="commit unavailable"):
        service.upload(meeting.id, "meeting.wav", "audio/wav", wav_bytes())

    assert db_session.query(Audio).count() == 0
    db_session.refresh(meeting)
    assert meeting.status == ProcessingStatus.CREATED.value
    assert list((tmp_path / "temp").glob("*")) == []
    assert list((tmp_path / "audio" / str(meeting.id)).glob("*")) == []
