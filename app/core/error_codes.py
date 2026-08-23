"""Stable error codes shown to operators and stored in diagnostics."""

from __future__ import annotations

from enum import StrEnum

from app.core.enums import JobType


class ErrorCode(StrEnum):
    """Short stable codes; technical exception text remains in the log file."""

    INTERNAL = "AMIP-001"
    DATABASE_UNAVAILABLE = "AMIP-002"
    WORKER_FAILURE = "WORKER-001"
    HEARTBEAT_FAILURE = "WORKER-002"
    TRANSCRIPTION_FAILURE = "TRANSCRIBE-001"
    DIARIZATION_FAILURE = "DIARIZE-001"
    SUMMARY_FAILURE = "SUMMARY-001"
    EXPORT_FAILURE = "EXPORT-001"
    PIPELINE_FAILURE = "PIPELINE-001"
    AUDIO_FAILURE = "AUDIO-001"
    RUNTIME_DEPENDENCY = "RUNTIME-001"


def job_failure_code(job_type: JobType | str) -> ErrorCode:
    """Return the operator-facing code for a background job family."""
    value = job_type.value if isinstance(job_type, JobType) else str(job_type)
    mapping = {
        JobType.TRANSCRIBE.value: ErrorCode.TRANSCRIPTION_FAILURE,
        JobType.DIARIZE.value: ErrorCode.DIARIZATION_FAILURE,
        JobType.SUMMARIZE.value: ErrorCode.SUMMARY_FAILURE,
        JobType.EXPORT.value: ErrorCode.EXPORT_FAILURE,
        JobType.FULL_PIPELINE.value: ErrorCode.PIPELINE_FAILURE,
    }
    return mapping.get(value, ErrorCode.WORKER_FAILURE)
