"""
Application enumerations.
Defines all status enums and type constants used across the application.
"""

from enum import Enum


class ProcessingStatus(str, Enum):
    """Processing status for meetings and their pipelines.
    
    Represents the lifecycle of a meeting from creation through
    audio processing to final completion.
    
    Flow:
        CREATED -> RECORDING -> AUDIO_UPLOADED -> TRANSCRIBING
        -> DIARIZING -> SUMMARIZING -> COMPLETED
        
        Any state -> FAILED (on error)
    """
    
    CREATED = "CREATED"
    RECORDING = "RECORDING"
    AUDIO_UPLOADED = "AUDIO_UPLOADED"
    TRANSCRIBING = "TRANSCRIBING"
    DIARIZING = "DIARIZING"
    SUMMARIZING = "SUMMARIZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    
    @classmethod
    def terminal_states(cls) -> list:
        """Get terminal (final) states.
        
        Returns:
            List of terminal status values
        """
        return [cls.COMPLETED, cls.FAILED]
    
    @classmethod
    def active_states(cls) -> list:
        """Get active (non-terminal) states.
        
        Returns:
            List of active status values
        """
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
        """Get states that indicate active processing.
        
        Returns:
            List of processing status values
        """
        return [
            cls.TRANSCRIBING,
            cls.DIARIZING,
            cls.SUMMARIZING,
        ]
    
    def can_transition_to(self, target: "ProcessingStatus") -> bool:
        """Check if transition to target state is valid.
        
        Args:
            target: Target status to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = {
            self.CREATED: [self.RECORDING, self.AUDIO_UPLOADED, self.FAILED],
            self.RECORDING: [self.AUDIO_UPLOADED, self.FAILED],
            self.AUDIO_UPLOADED: [self.TRANSCRIBING, self.FAILED],
            self.TRANSCRIBING: [self.DIARIZING, self.FAILED],
            self.DIARIZING: [self.SUMMARIZING, self.FAILED],
            self.SUMMARIZING: [self.COMPLETED, self.FAILED],
            self.COMPLETED: [],
            self.FAILED: [self.AUDIO_UPLOADED],  # Allow retry from failed
        }
        return target in valid_transitions.get(self, [])


class JobStatus(str, Enum):
    """Status for background jobs.
    
    Tracks the lifecycle of async processing jobs.
    """
    
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class JobType(str, Enum):
    """Types of background jobs.
    
    Defines the different processing tasks that can be queued.
    """
    
    TRANSCRIBE = "TRANSCRIBE"
    DIARIZE = "DIARIZE"
    SUMMARIZE = "SUMMARIZE"
    EXPORT = "EXPORT"
    FULL_PIPELINE = "FULL_PIPELINE"


class AudioFormat(str, Enum):
    """Supported audio formats.
    
    Defines the file types accepted for processing.
    """
    
    MP3 = "audio/mpeg"
    WAV = "audio/wav"
    M4A = "audio/mp4"
    WEBM = "audio/webm"
    OGG = "audio/ogg"
    FLAC = "audio/flac"


class ExportFormat(str, Enum):
    """Supported export formats.
    
    Defines the output formats for meeting reports.
    """
    
    MARKDOWN = "markdown"
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"


class Language(str, Enum):
    """Common language codes for transcription.
    
    Standard ISO 639-1 language codes.
    """
    
    AUTO = "auto"
    PORTUGUESE = "pt"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
