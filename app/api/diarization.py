"""HTTP API for persisted speaker diarization."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import require_meeting_access
from app.database.session import get_db
from app.models.meeting import Meeting
from app.schemas.diarization import DiarizationResponse, SpeakerSegmentResponse
from app.schemas.participant import ParticipantResponse
from app.services.diarization_service import DiarizationService
from app.services.participant_service import ParticipantService

router = APIRouter(prefix="/api/meetings", tags=["diarization"])


@router.get("/{meeting_id}/diarization", response_model=DiarizationResponse)
def get_diarization(
    meeting_id: int,
    _meeting: Meeting = Depends(require_meeting_access),
    db: Session = Depends(get_db),
) -> DiarizationResponse:
    rows = DiarizationService(db).get_by_meeting(meeting_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Diarization not found")

    participants = ParticipantService(db).list_by_meeting(meeting_id)
    by_label = {row.speaker_label: row for row in participants}
    segments: list[SpeakerSegmentResponse] = []
    for row in rows:
        participant = by_label.get(row.speaker_label)
        segments.append(
            SpeakerSegmentResponse(
                id=row.id,
                transcription_id=row.transcription_id,
                speaker_label=row.speaker_label,
                start_time=row.start_time,
                end_time=row.end_time,
                text=row.text,
                confidence=row.confidence,
                participant_name=participant.display_name if participant else None,
                participant_confirmed=participant.confirmed if participant else False,
            )
        )

    labels = {row.speaker_label for row in rows}
    return DiarizationResponse(
        meeting_id=meeting_id,
        num_speakers=len(labels),
        participants=[ParticipantResponse.model_validate(row) for row in participants],
        segments=segments,
    )
