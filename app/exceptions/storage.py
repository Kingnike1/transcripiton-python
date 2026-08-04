"""
Storage-related exceptions.
"""

from app.exceptions.base import AMIPError


class StorageError(AMIPError):
    """Base exception for storage operation failures.
    
    Example:
        raise StorageError("Disk space insufficient")
    """
    pass


class FileNotFoundError(StorageError):
    """Raised when a file is not found in storage.
    
    Example:
        raise FileNotFoundError("File not found: audio/meeting_123.mp3")
    """
    pass


class FileOperationError(StorageError):
    """Raised when a file operation fails.
    
    Example:
        raise FileOperationError("Failed to write file to disk")
    """
    pass
