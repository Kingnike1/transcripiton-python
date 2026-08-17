"""HTTP API for persisted meeting intelligence."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.analysis import MeetingAnalysisResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/meetings", tags=["analysis"])


@router.get("/{meeting_id}/analysis", response_model=MeetingAnalysisResponse)
def get_analysis(meeting_id: int, db: Session = Depends(get_db)) -> MeetingAnalysisResponse:
    service = AnalysisService(db)
    row = service.get_by_meeting(meeting_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return service.to_response(row)
