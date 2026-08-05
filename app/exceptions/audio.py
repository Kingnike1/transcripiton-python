"""Audio-related exceptions."""

from app.exceptions.base import AMIPError


class AudioError(AMIPError):
    """Base exception for audio-related errors."""


class RecordingError(AudioError):
    """Raised when audio recording fails."""


class AudioUploadError(AudioError):
    """Raised when an audio upload cannot be accepted."""


class AudioFormatError(AudioUploadError):
    """Raised when filename, MIME type, and content are inconsistent."""


class MeetingNotFoundError(AudioError):
    """Raised when an audio operation targets an unknown meeting."""


class AudioAlreadyExistsError(AudioUploadError):
    """Raised when a meeting already owns an active audio file."""
