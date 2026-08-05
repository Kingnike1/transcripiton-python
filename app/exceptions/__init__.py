"""Exception package for AMIP."""

from app.exceptions.base import AMIPError
from app.exceptions.database import DatabaseError, RecordNotFoundError, RecordAlreadyExistsError
from app.exceptions.audio import (
    AudioError,
    RecordingError,
    AudioUploadError,
    AudioFormatError,
    MeetingNotFoundError,
    AudioAlreadyExistsError,
)
from app.exceptions.pipeline import (
    PipelineError,
    TranscriptionError,
    DiarizationError,
    SummarizationError,
    InvalidStatusTransitionError,
)
from app.exceptions.validation import ValidationError, InvalidInputError, InvalidConfigurationError
from app.exceptions.storage import StorageError, FileNotFoundError, FileOperationError
from app.exceptions.export import ExportError, UnsupportedFormatError, ExportGenerationError

__all__ = [
    "AMIPError",
    "DatabaseError",
    "RecordNotFoundError",
    "RecordAlreadyExistsError",
    "AudioError",
    "RecordingError",
    "AudioUploadError",
    "AudioFormatError",
    "MeetingNotFoundError",
    "AudioAlreadyExistsError",
    "PipelineError",
    "TranscriptionError",
    "DiarizationError",
    "SummarizationError",
    "InvalidStatusTransitionError",
    "ValidationError",
    "InvalidInputError",
    "InvalidConfigurationError",
    "StorageError",
    "FileNotFoundError",
    "FileOperationError",
    "ExportError",
    "UnsupportedFormatError",
    "ExportGenerationError",
]
