"""HTTP API for persisted speaker diarization."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.diarization import DiarizationResponse, SpeakerSegmentResponse
from app.services.diarization_service import DiarizationService

router = APIRouter(prefix="/api/meetings", tags=["diarization"])


@router.get("/{meeting_id}/diarization", response_model=DiarizationResponse)
def get_diarization(meeting_id: int, db: Session = Depends(get_db)) -> DiarizationResponse:
    rows = DiarizationService(db).get_by_meeting(meeting_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Diarization not found")
    labels = {row.speaker_label for row in rows}
    return DiarizationResponse(
        meeting_id=meeting_id,
        num_speakers=len(labels),
        segments=[SpeakerSegmentResponse.model_validate(row) for row in rows],
    )
