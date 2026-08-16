"""Abstract provider contracts and pipeline value objects."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class AudioRecording:
    id: str
    file_path: str
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class TranscriptSegment:
    text: str
    start_time: float
    end_time: float
    speaker_label: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class TranscriptResult:
    id: str
    audio_path: str
    text: str
    language: Optional[str] = None
    segments: Optional[list[TranscriptSegment]] = None
    created_at: Optional[datetime] = None


@dataclass
class SpeakerSegment:
    start_time: float
    end_time: float
    speaker_label: str
    confidence: Optional[float] = None


@dataclass
class DiarizationResult:
    id: str
    audio_path: str
    segments: Optional[list[SpeakerSegment]] = None
    num_speakers: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class AIAnalysisResult:
    id: str
    transcript_path: str
    summary: Optional[str] = None
    action_items: Optional[list[str]] = None
    decisions: Optional[list[str]] = None
    risks: Optional[list[str]] = None
    open_questions: Optional[list[str]] = None
    follow_up_tasks: Optional[list[str]] = None
    created_at: Optional[datetime] = None


@dataclass
class ExportResult:
    id: str
    meeting_id: int
    format: str
    file_path: str
    file_size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None


class IAudioRecorder(ABC):
    """Legacy backend recording contract; browser capture is planned for frontend."""

    @abstractmethod
    def start_recording(self, meeting_id: int) -> AudioRecording:
        raise NotImplementedError

    @abstractmethod
    def stop_recording(self, recording_id: str) -> AudioRecording:
        raise NotImplementedError

    @abstractmethod
    def is_recording(self, recording_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_active_recordings(self) -> list[AudioRecording]:
        raise NotImplementedError


class ITranscriber(ABC):
    """Speech-to-text provider contract."""

    @abstractmethod
    def transcribe(self, audio_path: str, language: str = "auto") -> TranscriptResult:
        raise NotImplementedError

    @abstractmethod
    def transcribe_async(self, audio_path: str, language: str = "auto") -> str:
        raise NotImplementedError

    @abstractmethod
    def get_transcription_status(self, job_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def detect_language(self, audio_path: str) -> str:
        raise NotImplementedError


class ISpeakerIdentifier(ABC):
    """Speaker diarization provider contract."""

    @abstractmethod
    def diarize(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
    ) -> DiarizationResult:
        raise NotImplementedError

    @abstractmethod
    def diarize_async(self, audio_path: str, num_speakers: Optional[int] = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_diarization_status(self, job_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def count_speakers(self, audio_path: str) -> int:
        raise NotImplementedError


class IAISummarizer(ABC):
    """Meeting-analysis provider contract."""

    @abstractmethod
    def summarize(self, transcript_text: str) -> AIAnalysisResult:
        raise NotImplementedError

    @abstractmethod
    def summarize_async(self, transcript_text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_summarization_status(self, job_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_summary_only(self, transcript_text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def extract_action_items(self, transcript_text: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def extract_decisions(self, transcript_text: str) -> list[str]:
        raise NotImplementedError


class IExporter(ABC):
    """Meeting report export provider contract."""

    @abstractmethod
    def export(
        self,
        meeting_id: int,
        format: str,
        analysis: Optional[AIAnalysisResult] = None,
    ) -> ExportResult:
        raise NotImplementedError

    @abstractmethod
    def export_transcript_only(self, meeting_id: int, format: str) -> ExportResult:
        raise NotImplementedError

    @abstractmethod
    def export_analysis_only(self, meeting_id: int, format: str) -> ExportResult:
        raise NotImplementedError

    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        raise NotImplementedError
