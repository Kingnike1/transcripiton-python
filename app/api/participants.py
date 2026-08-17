"""HTTP API for participant identity mapping."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.meeting import Meeting
from app.schemas.participant import (
    ParticipantListResponse,
    ParticipantResponse,
    ParticipantUpdate,
)
from app.services.participant_service import ParticipantService

router = APIRouter(prefix="/api/meetings", tags=["participants"])


@router.get("/{meeting_id}/participants", response_model=ParticipantListResponse)
def get_participants(
    meeting_id: int,
    db: Session = Depends(get_db),
) -> ParticipantListResponse:
    if db.get(Meeting, meeting_id) is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    rows = ParticipantService(db).list_by_meeting(meeting_id)
    return ParticipantListResponse(
        meeting_id=meeting_id,
        participants=[ParticipantResponse.model_validate(row) for row in rows],
    )


@router.patch(
    "/{meeting_id}/participants/{speaker_label}",
    response_model=ParticipantResponse,
)
def update_participant(
    meeting_id: int,
    speaker_label: str,
    payload: ParticipantUpdate,
    db: Session = Depends(get_db),
) -> ParticipantResponse:
    service = ParticipantService(db)
    try:
        row = service.update_identity(
            meeting_id,
            speaker_label,
            display_name=payload.display_name,
            confirmed=payload.confirmed,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ParticipantResponse.model_validate(row)
