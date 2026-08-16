"""HTTP API for persisted transcriptions."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_transcription_service
from app.schemas.transcription import TranscriptionResponse
from app.services.transcription_service import TranscriptionService

router = APIRouter(prefix="/api", tags=["transcriptions"])


@router.get(
    "/meetings/{meeting_id}/transcription",
    response_model=TranscriptionResponse,
)
def get_meeting_transcription(
    meeting_id: int,
    service: TranscriptionService = Depends(get_transcription_service),
) -> TranscriptionResponse:
    transcription = service.get_by_meeting(meeting_id)
    if transcription is None:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return TranscriptionResponse.model_validate(transcription)
