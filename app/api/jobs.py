"""HTTP API for durable background jobs."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_job_service, require_job_access, require_meeting_access
from app.core.enums import JobType, ProcessingStatus
from app.models.meeting import Meeting
from app.models.processing_job import ProcessingJob
from app.schemas.jobs import ProcessingJobListResponse, ProcessingJobResponse
from app.services.persistent_job_service import PersistentJobService

router = APIRouter(prefix="/api", tags=["jobs"])


@router.post(
    "/meetings/{meeting_id}/jobs/transcription",
    response_model=ProcessingJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transcription_job(
    meeting_id: int,
    _meeting: Meeting = Depends(require_meeting_access),
    service: PersistentJobService = Depends(get_job_service),
) -> ProcessingJobResponse:
    audio = service.uow.audios.get_by_meeting_id(meeting_id)
    if audio is None:
        raise HTTPException(status_code=409, detail="Meeting has no uploaded audio")
    job = service.create_job(meeting_id, JobType.TRANSCRIBE, {"audio_id": audio.id})
    return ProcessingJobResponse.model_validate(job)


@router.post(
    "/meetings/{meeting_id}/jobs/diarization",
    response_model=ProcessingJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_diarization_job(
    meeting_id: int,
    meeting: Meeting = Depends(require_meeting_access),
    service: PersistentJobService = Depends(get_job_service),
) -> ProcessingJobResponse:
    transcription = service.uow.transcriptions.get_by_meeting_id(meeting_id)
    if transcription is None:
        raise HTTPException(status_code=409, detail="Meeting has no transcription")
    if meeting.status not in {ProcessingStatus.TRANSCRIBED.value, ProcessingStatus.DIARIZING.value}:
        raise HTTPException(status_code=409, detail="Meeting is not ready for diarization")
    job = service.create_job(meeting_id, JobType.DIARIZE, {"transcription_id": transcription.id})
    return ProcessingJobResponse.model_validate(job)


@router.post(
    "/meetings/{meeting_id}/jobs/analysis",
    response_model=ProcessingJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_analysis_job(
    meeting_id: int,
    meeting: Meeting = Depends(require_meeting_access),
    service: PersistentJobService = Depends(get_job_service),
) -> ProcessingJobResponse:
    if meeting.status not in {ProcessingStatus.DIARIZED.value, ProcessingStatus.SUMMARIZING.value}:
        raise HTTPException(status_code=409, detail="Meeting is not ready for LLM analysis")
    job = service.create_job(meeting_id, JobType.SUMMARIZE, {})
    return ProcessingJobResponse.model_validate(job)


@router.get("/jobs/{job_id}", response_model=ProcessingJobResponse)
def get_job(
    job_id: str,
    job: ProcessingJob = Depends(require_job_access),
) -> ProcessingJobResponse:
    return ProcessingJobResponse.model_validate(job)


@router.get("/meetings/{meeting_id}/jobs", response_model=ProcessingJobListResponse)
def get_meeting_jobs(
    meeting_id: int,
    _meeting: Meeting = Depends(require_meeting_access),
    service: PersistentJobService = Depends(get_job_service),
) -> ProcessingJobListResponse:
    jobs = service.get_jobs_by_meeting(meeting_id)
    return ProcessingJobListResponse(
        meeting_id=meeting_id,
        jobs=[ProcessingJobResponse.model_validate(job) for job in jobs],
    )


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_job(
    job_id: str,
    _job: ProcessingJob = Depends(require_job_access),
    service: PersistentJobService = Depends(get_job_service),
) -> None:
    if not service.cancel(job_id):
        raise HTTPException(status_code=409, detail="Only pending or retrying jobs can be cancelled")
