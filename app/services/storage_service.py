"""
Storage service module.
Manages file storage structure and operations.
"""

import shutil
import logging
from pathlib import Path
from typing import Optional
from uuid import uuid4

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing file storage.
    
    Provides methods to create directories, store files,
    retrieve files, and clean up temporary files.
    
    Directory structure:
        storage/
            audio/
            transcripts/
            exports/
            temp/
            logs/
    """
    
    # Directory constants
    AUDIO_DIR = "audio"
    TRANSCRIPTS_DIR = "transcripts"
    EXPORTS_DIR = "exports"
    TEMP_DIR = "temp"
    LOGS_DIR = "logs"
    
    def __init__(self, base_path: str = settings.STORAGE_PATH):
        """Initialize storage service.
        
        Args:
            base_path: Base storage directory path
        """
        self.base_path = Path(base_path)
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create all required storage directories.
        
        Creates the base storage path and all subdirectories
        if they don't already exist.
        """
        directories = [
            self.base_path / self.AUDIO_DIR,
            self.base_path / self.TRANSCRIPTS_DIR,
            self.base_path / self.EXPORTS_DIR,
            self.base_path / self.TEMP_DIR,
            self.base_path / self.LOGS_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def get_path(self, subdirectory: str, filename: Optional[str] = None) -> Path:
        """Get full path for a file in storage.
        
        Args:
            subdirectory: Subdirectory name (e.g., 'audio', 'transcripts')
            filename: Optional filename
            
        Returns:
            Full path object
        """
        path = self.base_path / subdirectory
        if filename:
            path = path / filename
        return path
    
    def store_audio(self, file_content: bytes, original_name: str, meeting_id: int) -> str:
        """Store an audio file.
        
        Args:
            file_content: Audio file bytes
            original_name: Original filename
            meeting_id: Meeting ID for organization
            
        Returns:
            Relative path to stored file
        """
        # Create meeting-specific subdirectory
        meeting_dir = self.get_path(self.AUDIO_DIR) / str(meeting_id)
        meeting_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename preserving extension
        ext = Path(original_name).suffix
        filename = f"{uuid4()}{ext}"
        file_path = meeting_dir / filename
        
        # Write file
        file_path.write_bytes(file_content)
        logger.info(f"Stored audio: {file_path}")
        
        # Return relative path
        return str(file_path.relative_to(self.base_path))
    
    def store_transcript(self, meeting_id: int, content: str, filename: str) -> str:
        """Store a transcript file.
        
        Args:
            meeting_id: Meeting ID for organization
            content: Transcript content
            filename: Filename for the transcript
            
        Returns:
            Relative path to stored file
        """
        meeting_dir = self.get_path(self.TRANSCRIPTS_DIR) / str(meeting_id)
        meeting_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = meeting_dir / filename
        file_path.write_text(content, encoding="utf-8")
        logger.info(f"Stored transcript: {file_path}")
        
        return str(file_path.relative_to(self.base_path))
    
    def store_export(self, meeting_id: int, content: bytes, filename: str) -> str:
        """Store an export file.
        
        Args:
            meeting_id: Meeting ID for organization
            content: Export file content
            filename: Filename for the export
            
        Returns:
            Relative path to stored file
        """
        meeting_dir = self.get_path(self.EXPORTS_DIR) / str(meeting_id)
        meeting_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = meeting_dir / filename
        file_path.write_bytes(content)
        logger.info(f"Stored export: {file_path}")
        
        return str(file_path.relative_to(self.base_path))
    
    def store_temp(self, filename: str, content: bytes) -> str:
        """Store a temporary file.
        
        Args:
            filename: Filename for the temp file
            content: File content
            
        Returns:
            Relative path to stored file
        """
        file_path = self.get_path(self.TEMP_DIR) / filename
        file_path.write_bytes(content)
        
        return str(file_path.relative_to(self.base_path))
    
    def read_file(self, relative_path: str) -> bytes:
        """Read file content from storage.
        
        Args:
            relative_path: Path relative to base storage
            
        Returns:
            File content as bytes
        """
        file_path = self.base_path / relative_path
        return file_path.read_bytes()
    
    def read_text(self, relative_path: str) -> str:
        """Read text file content from storage.
        
        Args:
            relative_path: Path relative to base storage
            
        Returns:
            File content as string
        """
        file_path = self.base_path / relative_path
        return file_path.read_text(encoding="utf-8")
    
    def delete_file(self, relative_path: str) -> bool:
        """Delete a file from storage.
        
        Args:
            relative_path: Path relative to base storage
            
        Returns:
            True if deleted, False if file not found
        """
        file_path = self.base_path / relative_path
        
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")
            return True
        
        return False
    
    def delete_directory(self, relative_path: str) -> bool:
        """Delete a directory and its contents from storage.
        
        Args:
            relative_path: Path relative to base storage
            
        Returns:
            True if deleted, False if directory not found
        """
        dir_path = self.base_path / relative_path
        
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)
            logger.info(f"Deleted directory: {dir_path}")
            return True
        
        return False
    
    def list_files(self, subdirectory: str, extension: Optional[str] = None) -> list:
        """List files in a subdirectory.
        
        Args:
            subdirectory: Subdirectory name
            extension: Optional file extension filter (e.g., '.mp3')
            
        Returns:
            List of filenames
        """
        dir_path = self.base_path / subdirectory
        
        if not dir_path.exists():
            return []
        
        files = []
        for item in dir_path.iterdir():
            if item.is_file():
                if extension is None or item.suffix == extension:
                    files.append(item.name)
        
        return files
    
    def get_file_size(self, relative_path: str) -> int:
        """Get file size in bytes.
        
        Args:
            relative_path: Path relative to base storage
            
        Returns:
            File size in bytes, 0 if not found
        """
        file_path = self.base_path / relative_path
        
        if file_path.exists():
            return file_path.stat().st_size
        
        return 0
    
    def file_exists(self, relative_path: str) -> bool:
        """Check if a file exists in storage.
        
        Args:
            relative_path: Path relative to base storage
            
        Returns:
            True if file exists, False otherwise
        """
        return (self.base_path / relative_path).exists()
    
    def cleanup_temp(self) -> int:
        """Clean up all temporary files.
        
        Returns:
            Number of files cleaned up
        """
        temp_dir = self.base_path / self.TEMP_DIR
        count = 0
        
        if temp_dir.exists():
            for item in temp_dir.iterdir():
                if item.is_file():
                    item.unlink()
                    count += 1
        
        logger.info(f"Cleaned up {count} temp files")
        return count
    
    def get_storage_info(self) -> dict:
        """Get storage usage information.
        
        Returns:
            Dictionary with storage statistics
        """
        info = {}
        
        for subdir in [
            self.AUDIO_DIR,
            self.TRANSCRIPTS_DIR,
            self.EXPORTS_DIR,
            self.TEMP_DIR,
        ]:
            dir_path = self.base_path / subdir
            total_size = 0
            file_count = 0
            
            if dir_path.exists():
                for item in dir_path.rglob("*"):
                    if item.is_file():
                        total_size += item.stat().st_size
                        file_count += 1
            
            info[subdir] = {
                "file_count": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
            }
        
        return info
