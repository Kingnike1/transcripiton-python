"""
Audio-related exceptions.
"""

from app.exceptions.base import AMIPError


class AudioError(AMIPError):
    """Base exception for audio-related errors.
    
    Example:
        raise AudioError("Audio processing failed")
    """
    pass


class RecordingError(AudioError):
    """Raised when audio recording fails.
    
    Example:
        raise RecordingError("Microphone not available")
    """
    pass


class AudioUploadError(AudioError):
    """Raised when audio upload fails.
    
    Example:
        raise AudioUploadError("File size exceeds maximum limit")
    """
    pass


class AudioFormatError(AudioError):
    """Raised when audio format is not supported.
    
    Example:
        raise AudioFormatError("Format .flac is not supported")
    """
    pass
