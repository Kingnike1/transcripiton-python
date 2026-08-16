"""Tests for processing, job, and export enums."""

from app.core.enums import ExportFormat, JobStatus, JobType, ProcessingStatus


class TestProcessingStatus:
    def test_all_status_values_exist(self):
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
        terminals = ProcessingStatus.terminal_states()
        assert ProcessingStatus.COMPLETED in terminals
        assert ProcessingStatus.FAILED in terminals
        assert ProcessingStatus.TRANSCRIBING not in terminals

    def test_active_states(self):
        active = ProcessingStatus.active_states()
        assert ProcessingStatus.CREATED in active
        assert ProcessingStatus.TRANSCRIBING in active
        assert ProcessingStatus.COMPLETED not in active
        assert ProcessingStatus.FAILED not in active

    def test_processing_states(self):
        processing = ProcessingStatus.processing_states()
        assert ProcessingStatus.TRANSCRIBING in processing
        assert ProcessingStatus.DIARIZING in processing
        assert ProcessingStatus.SUMMARIZING in processing
        assert ProcessingStatus.CREATED not in processing

    def test_valid_transitions(self):
        assert ProcessingStatus.CREATED.can_transition_to(ProcessingStatus.RECORDING)
        assert ProcessingStatus.CREATED.can_transition_to(ProcessingStatus.AUDIO_UPLOADED)
        assert ProcessingStatus.RECORDING.can_transition_to(ProcessingStatus.AUDIO_UPLOADED)
        assert ProcessingStatus.AUDIO_UPLOADED.can_transition_to(ProcessingStatus.TRANSCRIBING)
        assert ProcessingStatus.TRANSCRIBING.can_transition_to(ProcessingStatus.DIARIZING)
        assert ProcessingStatus.DIARIZING.can_transition_to(ProcessingStatus.SUMMARIZING)
        assert ProcessingStatus.SUMMARIZING.can_transition_to(ProcessingStatus.COMPLETED)

    def test_invalid_transitions(self):
        assert not ProcessingStatus.COMPLETED.can_transition_to(ProcessingStatus.SUMMARIZING)
        assert not ProcessingStatus.TRANSCRIBING.can_transition_to(ProcessingStatus.AUDIO_UPLOADED)
        assert not ProcessingStatus.DIARIZING.can_transition_to(ProcessingStatus.TRANSCRIBING)
        assert not ProcessingStatus.COMPLETED.can_transition_to(ProcessingStatus.CREATED)

    def test_any_state_can_fail(self):
        for status in ProcessingStatus:
            if status not in ProcessingStatus.terminal_states():
                assert status.can_transition_to(ProcessingStatus.FAILED)

    def test_failed_can_retry(self):
        assert ProcessingStatus.FAILED.can_transition_to(ProcessingStatus.AUDIO_UPLOADED)

    def test_completed_is_final(self):
        for status in ProcessingStatus:
            if status != ProcessingStatus.COMPLETED:
                assert not ProcessingStatus.COMPLETED.can_transition_to(status)


class TestJobStatus:
    def test_all_values_exist(self):
        assert JobStatus.PENDING.value == "PENDING"
        assert JobStatus.RUNNING.value == "RUNNING"
        assert JobStatus.COMPLETED.value == "COMPLETED"
        assert JobStatus.FAILED.value == "FAILED"
        assert JobStatus.CANCELLED.value == "CANCELLED"


class TestJobType:
    def test_all_values_exist(self):
        assert JobType.TRANSCRIBE.value == "TRANSCRIBE"
        assert JobType.DIARIZE.value == "DIARIZE"
        assert JobType.SUMMARIZE.value == "SUMMARIZE"
        assert JobType.EXPORT.value == "EXPORT"
        assert JobType.FULL_PIPELINE.value == "FULL_PIPELINE"


class TestExportFormat:
    def test_all_formats_exist(self):
        assert ExportFormat.MARKDOWN.value == "markdown"
        assert ExportFormat.PDF.value == "pdf"
        assert ExportFormat.TXT.value == "txt"
        assert ExportFormat.DOCX.value == "docx"
