"""
Exception package for AMIP.
Provides organized exception hierarchy for different error types.
"""

# Base exceptions
from app.exceptions.base import AMIPError

# Database exceptions
from app.exceptions.database import (
    DatabaseError,
    RecordNotFoundError,
    RecordAlreadyExistsError,
)

# Audio exceptions
from app.exceptions.audio import (
    AudioError,
    RecordingError,
    AudioUploadError,
    AudioFormatError,
)

# Pipeline exceptions
from app.exceptions.pipeline import (
    PipelineError,
    TranscriptionError,
    DiarizationError,
    SummarizationError,
    InvalidStatusTransitionError,
)

# Validation exceptions
from app.exceptions.validation import (
    ValidationError,
    InvalidInputError,
    InvalidConfigurationError,
)

# Storage exceptions
from app.exceptions.storage import (
    StorageError,
    FileNotFoundError,
    FileOperationError,
)

# Export exceptions
from app.exceptions.export import (
    ExportError,
    UnsupportedFormatError,
    ExportGenerationError,
)

__all__ = [
    # Base
    "AMIPError",
    # Database
    "DatabaseError",
    "RecordNotFoundError",
    "RecordAlreadyExistsError",
    # Audio
    "AudioError",
    "RecordingError",
    "AudioUploadError",
    "AudioFormatError",
    # Pipeline
    "PipelineError",
    "TranscriptionError",
    "DiarizationError",
    "SummarizationError",
    "InvalidStatusTransitionError",
    # Validation
    "ValidationError",
    "InvalidInputError",
    "InvalidConfigurationError",
    # Storage
    "StorageError",
    "FileNotFoundError",
    "FileOperationError",
    # Export
    "ExportError",
    "UnsupportedFormatError",
    "ExportGenerationError",
]
