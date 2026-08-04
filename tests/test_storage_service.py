"""
Tests for StorageService.
"""

import pytest
from pathlib import Path

from app.services.storage_service import StorageService


class TestStorageService:
    """Tests for StorageService."""
    
    @pytest.fixture
    def storage(self, tmp_path):
        """Create storage service with temp directory.
        
        Args:
            tmp_path: Pytest temp directory fixture
            
        Returns:
            StorageService instance
        """
        return StorageService(base_path=str(tmp_path))
    
    def test_ensures_directories(self, storage):
        """Test that all directories are created on init."""
        assert (storage.base_path / "audio").exists()
        assert (storage.base_path / "transcripts").exists()
        assert (storage.base_path / "exports").exists()
        assert (storage.base_path / "temp").exists()
        assert (storage.base_path / "logs").exists()
    
    def test_store_and_read_audio(self, storage):
        """Test storing and reading audio files."""
        # Arrange
        content = b"fake audio content"
        filename = "test.mp3"
        
        # Act
        path = storage.store_audio(content, filename, meeting_id=1)
        
        # Assert
        assert path is not None
        assert storage.file_exists(path)
        
        # Read back
        data = storage.read_file(path)
        assert data == content
    
    def test_store_transcript(self, storage):
        """Test storing transcript files."""
        # Arrange
        content = "This is a test transcript"
        filename = "transcript.txt"
        
        # Act
        path = storage.store_transcript(1, content, filename)
        
        # Assert
        assert path is not None
        assert storage.file_exists(path)
        assert storage.read_text(path) == content
    
    def test_store_export(self, storage):
        """Test storing export files."""
        # Arrange
        content = b"export content"
        filename = "report.md"
        
        # Act
        path = storage.store_export(1, content, filename)
        
        # Assert
        assert path is not None
        assert storage.file_exists(path)
    
    def test_store_temp(self, storage):
        """Test storing temporary files."""
        # Arrange
        content = b"temp content"
        filename = "temp_file.tmp"
        
        # Act
        path = storage.store_temp(filename, content)
        
        # Assert
        assert path is not None
        assert storage.file_exists(path)
    
    def test_delete_file(self, storage):
        """Test deleting a file."""
        # Arrange
        content = b"to be deleted"
        path = storage.store_temp("delete_me.tmp", content)
        assert storage.file_exists(path)
        
        # Act
        result = storage.delete_file(path)
        
        # Assert
        assert result is True
        assert not storage.file_exists(path)
    
    def test_delete_nonexistent_file(self, storage):
        """Test deleting a non-existent file."""
        result = storage.delete_file("nonexistent.txt")
        assert result is False
    
    def test_delete_directory(self, storage):
        """Test deleting a directory."""
        # Arrange
        dir_path = storage.base_path / "audio" / "999"
        dir_path.mkdir(parents=True)
        (dir_path / "test.mp3").write_bytes(b"data")
        
        # Act
        result = storage.delete_directory("audio/999")
        
        # Assert
        assert result is True
        assert not dir_path.exists()
    
    def test_get_file_size(self, storage):
        """Test getting file size."""
        # Arrange
        content = b"1234567890"
        path = storage.store_temp("sized.tmp", content)
        
        # Act
        size = storage.get_file_size(path)
        
        # Assert
        assert size == len(content)
    
    def test_get_file_size_nonexistent(self, storage):
        """Test getting size of non-existent file."""
        size = storage.get_file_size("nonexistent.txt")
        assert size == 0
    
    def test_list_files(self, storage):
        """Test listing files in a directory."""
        # Arrange
        storage.store_temp("file1.tmp", b"a")
        storage.store_temp("file2.tmp", b"b")
        
        # Act
        files = storage.list_files("temp")
        
        # Assert
        assert len(files) == 2
        assert "file1.tmp" in files
        assert "file2.tmp" in files
    
    def test_list_files_with_extension(self, storage):
        """Test listing files filtered by extension."""
        # Arrange
        storage.store_temp("file1.tmp", b"a")
        storage.store_temp("file2.txt", b"b")
        
        # Act
        files = storage.list_files("temp", extension=".txt")
        
        # Assert
        assert len(files) == 1
        assert "file2.txt" in files
    
    def test_cleanup_temp(self, storage):
        """Test cleaning up temporary files."""
        # Arrange
        storage.store_temp("temp1.tmp", b"a")
        storage.store_temp("temp2.tmp", b"b")
        
        # Act
        count = storage.cleanup_temp()
        
        # Assert
        assert count == 2
        files = storage.list_files("temp")
        assert len(files) == 0
    
    def test_get_storage_info(self, storage):
        """Test getting storage information."""
        # Arrange
        storage.store_temp("test.tmp", b"data")
        
        # Act
        info = storage.get_storage_info()
        
        # Assert
        assert "temp" in info
        assert info["temp"]["file_count"] == 1
        assert info["temp"]["total_size_bytes"] > 0
