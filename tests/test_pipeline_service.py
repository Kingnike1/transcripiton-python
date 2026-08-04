"""
Tests for PipelineService.
"""

import pytest

from app.services.pipeline_service import PipelineService
from app.services.interfaces import (
    ITranscriber,
    ISpeakerIdentifier,
    IAISummarizer,
    IExporter,
    TranscriptResult,
    DiarizationResult,
    AIAnalysisResult,
    ExportResult,
    TranscriptSegment,
    SpeakerSegment,
)


class MockTranscriber(ITranscriber):
    """Mock transcription implementation for testing."""
    
    def transcribe(self, audio_path, language="auto"):
        return TranscriptResult(
            id="test-1",
            audio_path=audio_path,
            text="This is a test transcription.",
            language="en",
            segments=[TranscriptSegment(text="Hello", start_time=0, end_time=1)],
        )
    
    def transcribe_async(self, audio_path, language="auto"):
        return "job-123"
    
    def get_transcription_status(self, job_id):
        return {"status": "completed"}
    
    def get_supported_languages(self):
        return ["en", "pt", "es"]
    
    def detect_language(self, audio_path):
        return "en"


class MockSpeakerIdentifier(ISpeakerIdentifier):
    """Mock speaker identifier implementation for testing."""
    
    def diarize(self, audio_path, num_speakers=None):
        return DiarizationResult(
            id="dia-1",
            audio_path=audio_path,
            segments=[SpeakerSegment(start_time=0, end_time=5, speaker_label="SPEAKER_00")],
            num_speakers=1,
        )
    
    def diarize_async(self, audio_path, num_speakers=None):
        return "job-456"
    
    def get_diarization_status(self, job_id):
        return {"status": "completed"}
    
    def count_speakers(self, audio_path):
        return 1


class MockSummarizer(IAISummarizer):
    """Mock summarizer implementation for testing."""
    
    def summarize(self, transcript_text):
        return AIAnalysisResult(
            id="sum-1",
            transcript_path="",
            summary="Test summary",
            action_items=["Action 1"],
            decisions=["Decision 1"],
            risks=[],
            open_questions=[],
            follow_up_tasks=["Task 1"],
        )
    
    def summarize_async(self, transcript_text):
        return "job-789"
    
    def get_summarization_status(self, job_id):
        return {"status": "completed"}
    
    def generate_summary_only(self, transcript_text):
        return "Summary only"
    
    def extract_action_items(self, transcript_text):
        return ["Action 1"]
    
    def extract_decisions(self, transcript_text):
        return ["Decision 1"]


class MockExporter(IExporter):
    """Mock exporter implementation for testing."""
    
    def export(self, meeting_id, format, analysis=None):
        return ExportResult(
            id="exp-1",
            meeting_id=meeting_id,
            format=format,
            file_path=f"/exports/meeting_{meeting_id}.{format}",
            file_size_bytes=1024,
        )
    
    def export_transcript_only(self, meeting_id, format):
        return ExportResult(
            id="exp-2",
            meeting_id=meeting_id,
            format=format,
            file_path=f"/exports/transcript_{meeting_id}.{format}",
        )
    
    def export_analysis_only(self, meeting_id, format):
        return ExportResult(
            id="exp-3",
            meeting_id=meeting_id,
            format=format,
            file_path=f"/exports/analysis_{meeting_id}.{format}",
        )
    
    def get_supported_formats(self):
        return ["markdown", "pdf", "txt", "docx"]


class TestPipelineService:
    """Tests for PipelineService."""
    
    @pytest.fixture
    def pipeline(self):
        """Create pipeline service with mock components."""
        p = PipelineService()
        p.register_transcriber(MockTranscriber())
        p.register_speaker_identifier(MockSpeakerIdentifier())
        p.register_summarizer(MockSummarizer())
        p.register_exporter(MockExporter())
        return p
    
    @pytest.fixture
    def empty_pipeline(self):
        """Create pipeline service without components."""
        return PipelineService()
    
    def test_register_transcriber(self, empty_pipeline):
        """Test registering a transcriber."""
        empty_pipeline.register_transcriber(MockTranscriber())
        assert empty_pipeline.can_process_transcription() is True
    
    def test_register_speaker_identifier(self, empty_pipeline):
        """Test registering a speaker identifier."""
        empty_pipeline.register_speaker_identifier(MockSpeakerIdentifier())
        assert empty_pipeline.can_process_diarization() is True
    
    def test_register_summarizer(self, empty_pipeline):
        """Test registering a summarizer."""
        empty_pipeline.register_summarizer(MockSummarizer())
        assert empty_pipeline.can_process_summarization() is True
    
    def test_register_exporter(self, empty_pipeline):
        """Test registering an exporter."""
        empty_pipeline.register_exporter(MockExporter())
        assert empty_pipeline.can_process_export() is True
    
    def test_no_components_registered(self, empty_pipeline):
        """Test pipeline with no components."""
        assert empty_pipeline.can_process_transcription() is False
        assert empty_pipeline.can_process_diarization() is False
        assert empty_pipeline.can_process_summarization() is False
        assert empty_pipeline.can_process_export() is False
    
    def test_pipeline_status_not_ready(self, empty_pipeline):
        """Test pipeline status when not all components are registered."""
        status = empty_pipeline.get_pipeline_status()
        assert status["ready"] is False
    
    def test_pipeline_status_ready(self, pipeline):
        """Test pipeline status when all components are registered."""
        status = pipeline.get_pipeline_status()
        assert status["ready"] is True
    
    def test_execute_transcription_step(self, pipeline):
        """Test executing transcription step."""
        result = pipeline.execute_transcription_step("audio/test.mp3")
        assert result is not None
        assert result["text"] == "This is a test transcription."
        assert result["language"] == "en"
    
    def test_execute_diarization_step(self, pipeline):
        """Test executing diarization step."""
        result = pipeline.execute_diarization_step("audio/test.mp3")
        assert result is not None
        assert result["num_speakers"] == 1
    
    def test_execute_summarization_step(self, pipeline):
        """Test executing summarization step."""
        result = pipeline.execute_summarization_step("Test transcript text")
        assert result is not None
        assert result["summary"] == "Test summary"
        assert len(result["action_items"]) == 1
    
    def test_execute_export_step(self, pipeline):
        """Test executing export step."""
        result = pipeline.execute_export_step(1, "markdown")
        assert result is not None
        assert result["format"] == "markdown"
    
    def test_transcription_unavailable(self, empty_pipeline):
        """Test transcription when not available."""
        result = empty_pipeline.execute_transcription_step("audio/test.mp3")
        assert result is None
    
    def test_diarization_unavailable(self, empty_pipeline):
        """Test diarization when not available."""
        result = empty_pipeline.execute_diarization_step("audio/test.mp3")
        assert result is None
    
    def test_summarization_unavailable(self, empty_pipeline):
        """Test summarization when not available."""
        result = empty_pipeline.execute_summarization_step("text")
        assert result is None
    
    def test_export_unavailable(self, empty_pipeline):
        """Test export when not available."""
        result = empty_pipeline.execute_export_step(1, "markdown")
        assert result is None
    
    def test_process_full_pipeline(self, pipeline):
        """Test processing the full pipeline."""
        result = pipeline.process_full_pipeline(1, "audio/test.mp3")
        
        assert result is not None
        assert result["meeting_id"] == 1
        assert "transcription" in result["steps"]
        assert "diarization" in result["steps"]
        assert "summarization" in result["steps"]
        assert result["steps"]["transcription"]["text"] is not None
