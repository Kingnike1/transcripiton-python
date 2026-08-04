"""
Application exceptions module.
Defines custom exception classes for all error types.
"""


class AMIPError(Exception):
    """Base exception for all AMIP errors.
    
    All custom exceptions inherit from this base class
    to allow consistent error handling.
    """
    
    def __init__(self, message: str, details: str = ""):
        """Initialize AMIP error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


class RecordingError(AMIPError):
    """Raised when audio recording fails.
    
    Example:
        raise RecordingError("Microphone not available")
    """
    pass


class TranscriptionError(AMIPError):
    """Raised when speech-to-text transcription fails.
    
    Example:
        raise TranscriptionError("Audio file corrupted")
    """
    pass


class DiarizationError(AMIPError):
    """Raised when speaker diarization fails.
    
    Example:
        raise DiarizationError("Cannot detect speakers")
    """
    pass


class SummarizationError(AMIPError):
    """Raised when AI summarization fails.
    
    Example:
        raise SummarizationError("API rate limit exceeded")
    """
    pass


class ExportError(AMIPError):
    """Raised when file export fails.
    
    Example:
        raise ExportError("Failed to generate PDF")
    """
    pass


class StorageError(AMIPError):
    """Raised when file storage operation fails.
    
    Example:
        raise StorageError("Disk space insufficient")
    """
    pass


class PipelineError(AMIPError):
    """Raised when pipeline processing fails.
    
    Example:
        raise PipelineError("Pipeline step timeout")
    """
    pass


class InvalidStatusTransitionError(AMIPError):
    """Raised when an invalid status transition is attempted.
    
    Example:
        raise InvalidStatusTransitionError("Cannot go from COMPLETED to TRANSCRIBING")
    """
    pass
