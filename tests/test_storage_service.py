"""Tests for StorageService."""

import pytest

from app.services.storage_service import StorageService


class TestStorageService:
    @pytest.fixture
    def storage(self, tmp_path):
        return StorageService(base_path=str(tmp_path))

    def test_ensures_directories(self, storage):
        assert (storage.base_path / "audio").exists()
        assert (storage.base_path / "transcripts").exists()
        assert (storage.base_path / "exports").exists()
        assert (storage.base_path / "temp").exists()
        assert (storage.base_path / "logs").exists()

    def test_store_and_read_audio(self, storage):
        content = b"fake audio content"
        path = storage.store_audio(content, "test.mp3", meeting_id=1)
        assert storage.file_exists(path)
        assert storage.read_file(path) == content

    def test_store_transcript(self, storage):
        content = "This is a test transcript"
        path = storage.store_transcript(1, content, "transcript.txt")
        assert storage.file_exists(path)
        assert storage.read_text(path) == content

    def test_store_export(self, storage):
        path = storage.store_export(1, b"export content", "report.md")
        assert storage.file_exists(path)

    def test_store_temp(self, storage):
        path = storage.store_temp("temp_file.tmp", b"temp content")
        assert storage.file_exists(path)

    def test_delete_file(self, storage):
        path = storage.store_temp("delete_me.tmp", b"to be deleted")
        assert storage.file_exists(path)
        assert storage.delete_file(path) is True
        assert not storage.file_exists(path)

    def test_delete_nonexistent_file(self, storage):
        assert storage.delete_file("nonexistent.txt") is False

    def test_delete_directory(self, storage):
        dir_path = storage.base_path / "audio" / "999"
        dir_path.mkdir(parents=True)
        (dir_path / "test.mp3").write_bytes(b"data")
        assert storage.delete_directory("audio/999") is True
        assert not dir_path.exists()

    def test_get_file_size(self, storage):
        content = b"1234567890"
        path = storage.store_temp("sized.tmp", content)
        assert storage.get_file_size(path) == len(content)

    def test_get_file_size_nonexistent(self, storage):
        assert storage.get_file_size("nonexistent.txt") == 0

    def test_list_files(self, storage):
        storage.store_temp("file1.tmp", b"a")
        storage.store_temp("file2.tmp", b"b")
        files = storage.list_files("temp")
        assert len(files) == 2
        assert "file1.tmp" in files
        assert "file2.tmp" in files

    def test_list_files_with_extension(self, storage):
        storage.store_temp("file1.tmp", b"a")
        storage.store_temp("file2.txt", b"b")
        files = storage.list_files("temp", extension=".txt")
        assert files == ["file2.txt"]

    def test_cleanup_temp(self, storage):
        storage.store_temp("temp1.tmp", b"a")
        storage.store_temp("temp2.tmp", b"b")
        assert storage.cleanup_temp() == 2
        assert storage.list_files("temp") == []

    def test_get_storage_info(self, storage):
        storage.store_temp("test.tmp", b"data")
        info = storage.get_storage_info()
        assert "temp" in info
        assert info["temp"]["file_count"] == 1
        assert info["temp"]["total_size_bytes"] > 0
