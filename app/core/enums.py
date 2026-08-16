"""
Application enumerations.
Defines all status enums and type constants used across the application.
"""

from enum import Enum


class ProcessingStatus(str, Enum):
    """Processing status for meetings and their pipelines."""

    CREATED = "CREATED"
    RECORDING = "RECORDING"
    AUDIO_UPLOADED = "AUDIO_UPLOADED"
    TRANSCRIBING = "TRANSCRIBING"
    TRANSCRIBED = "TRANSCRIBED"
    DIARIZING = "DIARIZING"
    SUMMARIZING = "SUMMARIZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    @classmethod
    def terminal_states(cls) -> list:
        return [cls.TRANSCRIBED, cls.COMPLETED, cls.FAILED]

    @classmethod
    def active_states(cls) -> list:
        return [
            cls.CREATED,
            cls.RECORDING,
            cls.AUDIO_UPLOADED,
            cls.TRANSCRIBING,
            cls.DIARIZING,
            cls.SUMMARIZING,
        ]

    @classmethod
    def processing_states(cls) -> list:
        return [cls.TRANSCRIBING, cls.DIARIZING, cls.SUMMARIZING]

    def can_transition_to(self, target: "ProcessingStatus") -> bool:
        valid_transitions = {
            self.CREATED: [self.RECORDING, self.AUDIO_UPLOADED, self.FAILED],
            self.RECORDING: [self.AUDIO_UPLOADED, self.FAILED],
            self.AUDIO_UPLOADED: [self.TRANSCRIBING, self.FAILED],
            self.TRANSCRIBING: [self.TRANSCRIBED, self.FAILED],
            self.TRANSCRIBED: [self.DIARIZING, self.SUMMARIZING],
            self.DIARIZING: [self.SUMMARIZING, self.FAILED],
            self.SUMMARIZING: [self.COMPLETED, self.FAILED],
            self.COMPLETED: [],
            self.FAILED: [self.AUDIO_UPLOADED],
        }
        return target in valid_transitions.get(self, [])


class JobStatus(str, Enum):
    """Persistent background-job lifecycle."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class JobType(str, Enum):
    """Types of background jobs."""

    TRANSCRIBE = "TRANSCRIBE"
    DIARIZE = "DIARIZE"
    SUMMARIZE = "SUMMARIZE"
    EXPORT = "EXPORT"
    FULL_PIPELINE = "FULL_PIPELINE"


class AudioFormat(str, Enum):
    """Supported audio formats."""

    MP3 = "audio/mpeg"
    WAV = "audio/wav"
    M4A = "audio/mp4"
    WEBM = "audio/webm"
    OGG = "audio/ogg"
    FLAC = "audio/flac"


class ExportFormat(str, Enum):
    """Supported export formats."""

    MARKDOWN = "markdown"
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"


class Language(str, Enum):
    """Common language codes for transcription."""

    AUTO = "auto"
    PORTUGUESE = "pt"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
