"""
Tests for ProcessingStatus enum and transitions.
"""

import pytest

from app.core.enums import ProcessingStatus, JobStatus, JobType, ExportFormat


class TestProcessingStatus:
    """Tests for ProcessingStatus enum."""
    
    def test_all_status_values_exist(self):
        """Test that all expected status values exist."""
        expected = [
            "CREATED",
            "RECORDING",
            "AUDIO_UPLOADED",
            "TRANSCRIBING",
            "DIARIZING",
            "SUMMARIZING",
            "COMPLETED",
            "FAILED",
        ]
        
        for value in expected:
            assert ProcessingStatus(value) is not None
    
    def test_terminal_states(self):
        """Test terminal states classification."""
        terminals = ProcessingStatus.terminal_states()
        assert ProcessingStatus.COMPLETED in terminals
        assert ProcessingStatus.FAILED in terminals
        assert ProcessingStatus.TRANSCRIBING not in terminals
    
    def test_active_states(self):
        """Test active states classification."""
        active = ProcessingStatus.active_states()
        assert ProcessingStatus.CREATED in active
        assert ProcessingStatus.TRANSCRIBING in active
        assert ProcessingStatus.COMPLETED not in active
        assert ProcessingStatus.FAILED not in active
    
    def test_processing_states(self):
        """Test processing states classification."""
        processing = ProcessingStatus.processing_states()
        assert ProcessingStatus.TRANSCRIBING in processing
        assert ProcessingStatus.DIARIZING in processing
        assert ProcessingStatus.SUMMARIZING in processing
        assert ProcessingStatus.CREATED not in processing
    
    def test_valid_transitions(self):
        """Test valid status transitions."""
        # CREATED -> RECORDING
        assert ProcessingStatus.CREATED.can_transition_to(ProcessingStatus.RECORDING)
        # CREATED -> AUDIO_UPLOADED
        assert ProcessingStatus.CREATED.can_transition_to(ProcessingStatus.AUDIO_UPLOADED)
        # RECORDING -> AUDIO_UPLOADED
        assert ProcessingStatus.RECORDING.can_transition_to(ProcessingStatus.AUDIO_UPLOADED)
        # AUDIO_UPLOADED -> TRANSCRIBING
        assert ProcessingStatus.AUDIO_UPLOADED.can_transition_to(ProcessingStatus.TRANSCRIBING)
        # TRANSCRIBING -> DIARIZING
        assert ProcessingStatus.TRANSCRIBING.can_transition_to(ProcessingStatus.DIARIZING)
        # DIARIZING -> SUMMARIZING
        assert ProcessingStatus.DIARIZING.can_transition_to(ProcessingStatus.SUMMARIZING)
        # SUMMARIZING -> COMPLETED
        assert ProcessingStatus.SUMMARIZING.can_transition_to(ProcessingStatus.COMPLETED)
    
    def test_invalid_transitions(self):
        """Test invalid status transitions."""
        # Cannot go backward
        assert not ProcessingStatus.COMPLETED.can_transition_to(ProcessingStatus.SUMMARIZING)
        assert not ProcessingStatus.TRANSCRIBING.can_transition_to(ProcessingStatus.AUDIO_UPLOADED)
        assert not ProcessingStatus.DIARIZING.can_transition_to(ProcessingStatus.TRANSCRIBING)
        # Cannot go from terminal to active
        assert not ProcessingStatus.COMPLETED.can_transition_to(ProcessingStatus.CREATED)
    
    def test_any_state_can_fail(self):
        """Test that any non-terminal state can transition to FAILED."""
        for status in ProcessingStatus:
            if status not in ProcessingStatus.terminal_states():
                assert status.can_transition_to(ProcessingStatus.FAILED)
    
    def test_failed_can_retry(self):
        """Test that FAILED can transition back to AUDIO_UPLOADED for retry."""
        assert ProcessingStatus.FAILED.can_transition_to(ProcessingStatus.AUDIO_UPLOADED)
    
    def test_completed_is_final(self):
        """Test that COMPLETED cannot transition anywhere."""
        for status in ProcessingStatus:
            if status != ProcessingStatus.COMPLETED:
                assert not ProcessingStatus.COMPLETED.can_transition_to(status)


class TestJobStatus:
    """Tests for JobStatus enum."""
    
    def test_all_values_exist(self):
        """Test all job status values exist."""
        assert JobStatus.PENDING.value == "PENDING"
        assert JobStatus.RUNNING.value == "RUNNING"
        assert JobStatus.COMPLETED.value == "COMPLETED"
        assert JobStatus.FAILED.value == "FAILED"
        assert JobStatus.CANCELLED.value == "CANCELLED"


class TestJobType:
    """Tests for JobType enum."""
    
    def test_all_values_exist(self):
        """Test all job type values exist."""
        assert JobType.TRANSCRIBE.value == "TRANSCRIBE"
        assert JobType.DIARIZE.value == "DIARIZE"
        assert JobType.SUMMARIZE.value == "SUMMARIZE"
        assert JobType.EXPORT.value == "EXPORT"
        assert JobType.FULL_PIPELINE.value == "FULL_PIPELINE"


class TestExportFormat:
    """Tests for ExportFormat enum."""
    
    def test_all_formats_exist(self):
        """Test all export format values exist."""
        assert ExportFormat.MARKDOWN.value == "markdown"
        assert ExportFormat.PDF.value == "pdf"
        assert ExportFormat.TXT.value == "txt"
        assert ExportFormat.DOCX.value == "docx"
