"""
Pipeline processing exceptions.
"""

from app.exceptions.base import AMIPError


class PipelineError(AMIPError):
    """Base exception for pipeline processing errors.
    
    Example:
        raise PipelineError("Pipeline step timeout")
    """
    pass


class TranscriptionError(PipelineError):
    """Raised when speech-to-text transcription fails.
    
    Example:
        raise TranscriptionError("Audio file corrupted")
    """
    pass


class DiarizationError(PipelineError):
    """Raised when speaker diarization fails.
    
    Example:
        raise DiarizationError("Cannot detect speakers")
    """
    pass


class SummarizationError(PipelineError):
    """Raised when AI summarization fails.
    
    Example:
        raise SummarizationError("API rate limit exceeded")
    """
    pass


class InvalidStatusTransitionError(PipelineError):
    """Raised when an invalid status transition is attempted.
    
    Example:
        raise InvalidStatusTransitionError("Cannot go from COMPLETED to TRANSCRIBING")
    """
    pass
