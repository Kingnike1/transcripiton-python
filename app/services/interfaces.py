"""
Pipeline interfaces module.
Defines abstract contracts for all processing components.

These interfaces define the contracts that will be used by
future implementations. No concrete implementations are
provided in this module.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


# ============================================================================
# Data Classes for Pipeline Input/Output
# ============================================================================


@dataclass
class AudioRecording:
    """Represents an audio recording.
    
    Attributes:
        id: Unique identifier
        file_path: Path to audio file
        duration_seconds: Recording duration
        file_size_bytes: File size in bytes
        mime_type: Audio MIME type
        created_at: Recording timestamp
    """
    id: str
    file_path: str
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class TranscriptSegment:
    """Represents a segment of transcribed text.
    
    Attributes:
        text: Transcribed text
        start_time: Start time in seconds
        end_time: End time in seconds
        speaker_label: Speaker identifier
        confidence: Confidence score (0.0-1.0)
    """
    text: str
    start_time: float
    end_time: float
    speaker_label: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class TranscriptResult:
    """Represents a complete transcription result.
    
    Attributes:
        id: Unique identifier
        audio_path: Path to source audio
        text: Full transcribed text
        language: Detected language code
        segments: List of transcript segments
        created_at: Transcription timestamp
    """
    id: str
    audio_path: str
    text: str
    language: Optional[str] = None
    segments: List[TranscriptSegment] = None
    created_at: Optional[datetime] = None


@dataclass
class SpeakerSegment:
    """Represents a speaker diarization segment.
    
    Attributes:
        start_time: Start time in seconds
        end_time: End time in seconds
        speaker_label: Speaker identifier (e.g., SPEAKER_00)
        confidence: Confidence score
    """
    start_time: float
    end_time: float
    speaker_label: str
    confidence: Optional[float] = None


@dataclass
class DiarizationResult:
    """Represents a complete diarization result.
    
    Attributes:
        id: Unique identifier
        audio_path: Path to source audio
        segments: List of speaker segments
        num_speakers: Number of speakers detected
        created_at: Diarization timestamp
    """
    id: str
    audio_path: str
    segments: List[SpeakerSegment] = None
    num_speakers: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class AIAnalysisResult:
    """Represents AI analysis results.
    
    Attributes:
        id: Unique identifier
        transcript_path: Path to source transcript
        summary: Meeting summary
        action_items: List of action items
        decisions: List of decisions made
        risks: Identified risks
        open_questions: Unresolved questions
        follow_up_tasks: Follow-up tasks
        created_at: Analysis timestamp
    """
    id: str
    transcript_path: str
    summary: Optional[str] = None
    action_items: Optional[List[str]] = None
    decisions: Optional[List[str]] = None
    risks: Optional[List[str]] = None
    open_questions: Optional[List[str]] = None
    follow_up_tasks: Optional[List[str]] = None
    created_at: Optional[datetime] = None


@dataclass
class ExportResult:
    """Represents an export result.
    
    Attributes:
        id: Unique identifier
        meeting_id: Associated meeting ID
        format: Export format (markdown, pdf, txt, docx)
        file_path: Path to exported file
        file_size_bytes: Exported file size
        created_at: Export timestamp
    """
    id: str
    meeting_id: int
    format: str
    file_path: str
    file_size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None


# ============================================================================
# Abstract Interfaces
# ============================================================================


class IAudioRecorder(ABC):
    """Interface for audio recording functionality.
    
    Defines the contract for recording audio from microphone
    or other input sources. Future implementations may include
    browser-based recording, system audio capture, or file import.
    """
    
    @abstractmethod
    def start_recording(self, meeting_id: int) -> AudioRecording:
        """Start a new audio recording.
        
        Args:
            meeting_id: ID of the meeting being recorded
            
        Returns:
            AudioRecording with recording metadata
            
        Raises:
            RecordingError: If recording cannot be started
        """
        pass
    
    @abstractmethod
    def stop_recording(self, recording_id: str) -> AudioRecording:
        """Stop an active recording.
        
        Args:
            recording_id: ID of the recording to stop
            
        Returns:
            AudioRecording with final metadata (duration, size)
            
        Raises:
            RecordingError: If recording cannot be stopped
        """
        pass
    
    @abstractmethod
    def is_recording(self, recording_id: str) -> bool:
        """Check if a recording is currently active.
        
        Args:
            recording_id: ID of the recording to check
            
        Returns:
            True if recording is active, False otherwise
        """
        pass
    
    @abstractmethod
    def get_active_recordings(self) -> List[AudioRecording]:
        """Get all currently active recordings.
        
        Returns:
            List of active AudioRecording instances
        """
        pass


class ITranscriber(ABC):
    """Interface for speech-to-text transcription.
    
    Defines the contract for converting audio to text.
    Future implementations may include Whisper, Google STT,
    AWS Transcribe, or other providers.
    """
    
    @abstractmethod
    def transcribe(self, audio_path: str, language: str = "auto") -> TranscriptResult:
        """Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file
            language: Language code (default: auto-detect)
            
        Returns:
            TranscriptResult with transcribed text and segments
            
        Raises:
            TranscriptionError: If transcription fails
        """
        pass
    
    @abstractmethod
    def transcribe_async(self, audio_path: str, language: str = "auto") -> str:
        """Start async transcription and return job ID.
        
        Args:
            audio_path: Path to the audio file
            language: Language code
            
        Returns:
            Job ID for tracking progress
            
        Raises:
            TranscriptionError: If transcription cannot be started
        """
        pass
    
    @abstractmethod
    def get_transcription_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of an async transcription job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Dictionary with status and progress information
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages.
        
        Returns:
            List of language codes (e.g., ['en', 'pt', 'es'])
        """
        pass
    
    @abstractmethod
    def detect_language(self, audio_path: str) -> str:
        """Detect the language of an audio file.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            ISO 639-1 language code (e.g., 'en', 'pt')
            
        Raises:
            TranscriptionError: If language detection fails
        """
        pass


class ISpeakerIdentifier(ABC):
    """Interface for speaker diarization.
    
    Defines the contract for identifying and separating speakers
    in audio recordings. Future implementations may include
    pyannote.audio, NVIDIA NeMo, or other providers.
    """
    
    @abstractmethod
    def diarize(self, audio_path: str, num_speakers: Optional[int] = None) -> DiarizationResult:
        """Perform speaker diarization on audio file.
        
        Args:
            audio_path: Path to the audio file
            num_speakers: Expected number of speakers (optional)
            
        Returns:
            DiarizationResult with speaker segments
            
        Raises:
            DiarizationError: If diarization fails
        """
        pass
    
    @abstractmethod
    def diarize_async(self, audio_path: str, num_speakers: Optional[int] = None) -> str:
        """Start async diarization and return job ID.
        
        Args:
            audio_path: Path to the audio file
            num_speakers: Expected number of speakers
            
        Returns:
            Job ID for tracking progress
        """
        pass
    
    @abstractmethod
    def get_diarization_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of an async diarization job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Dictionary with status and progress information
        """
        pass
    
    @abstractmethod
    def count_speakers(self, audio_path: str) -> int:
        """Estimate the number of speakers in audio.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Estimated number of speakers
            
        Raises:
            DiarizationError: If speaker counting fails
        """
        pass


class IAISummarizer(ABC):
    """Interface for AI meeting summarization.
    
    Defines the contract for generating summaries, action items,
    decisions, and other meeting intelligence. Future implementations
    may include GPT-4, Ollama (Llama2), Claude, or other LLMs.
    """
    
    @abstractmethod
    def summarize(self, transcript_text: str) -> AIAnalysisResult:
        """Generate comprehensive meeting analysis.
        
        Generates summary, action items, decisions, risks,
        open questions, and follow-up tasks from transcript text.
        
        Args:
            transcript_text: Full transcribed meeting text
            
        Returns:
            AIAnalysisResult with all analysis fields
            
        Raises:
            SummarizationError: If analysis fails
        """
        pass
    
    @abstractmethod
    def summarize_async(self, transcript_text: str) -> str:
        """Start async summarization and return job ID.
        
        Args:
            transcript_text: Full transcribed meeting text
            
        Returns:
            Job ID for tracking progress
        """
        pass
    
    @abstractmethod
    def get_summarization_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of an async summarization job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Dictionary with status and progress information
        """
        pass
    
    @abstractmethod
    def generate_summary_only(self, transcript_text: str) -> str:
        """Generate a concise meeting summary.
        
        Args:
            transcript_text: Full transcribed meeting text
            
        Returns:
            Summary text
            
        Raises:
            SummarizationError: If summary generation fails
        """
        pass
    
    @abstractmethod
    def extract_action_items(self, transcript_text: str) -> List[str]:
        """Extract action items from transcript.
        
        Args:
            transcript_text: Full transcribed meeting text
            
        Returns:
            List of action items
            
        Raises:
            SummarizationError: If extraction fails
        """
        pass
    
    @abstractmethod
    def extract_decisions(self, transcript_text: str) -> List[str]:
        """Extract decisions made during the meeting.
        
        Args:
            transcript_text: Full transcribed meeting text
            
        Returns:
            List of decisions
            
        Raises:
            SummarizationError: If extraction fails
        """
        pass


class IExporter(ABC):
    """Interface for meeting report export.
    
    Defines the contract for exporting meeting data and analysis
    in various formats. Future implementations may include
    Markdown, PDF, TXT, DOCX, or other format exporters.
    """
    
    @abstractmethod
    def export(self, meeting_id: int, format: str, analysis: Optional[AIAnalysisResult] = None) -> ExportResult:
        """Export meeting report in specified format.
        
        Args:
            meeting_id: Meeting ID to export
            format: Export format (markdown, pdf, txt, docx)
            analysis: Optional AI analysis to include
            
        Returns:
            ExportResult with exported file path
            
        Raises:
            ExportError: If export fails
        """
        pass
    
    @abstractmethod
    def export_transcript_only(self, meeting_id: int, format: str) -> ExportResult:
        """Export meeting transcript only (without analysis).
        
        Args:
            meeting_id: Meeting ID
            format: Export format
            
        Returns:
            ExportResult with exported file path
        """
        pass
    
    @abstractmethod
    def export_analysis_only(self, meeting_id: int, format: str) -> ExportResult:
        """Export meeting analysis only (without transcript).
        
        Args:
            meeting_id: Meeting ID
            format: Export format
            
        Returns:
            ExportResult with exported file path
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats.
        
        Returns:
            List of format strings (e.g., ['markdown', 'pdf', 'txt', 'docx'])
        """
        pass
