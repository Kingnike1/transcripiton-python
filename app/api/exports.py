"""HTTP endpoint for meeting exports."""

from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_optional
from app.database.session import get_db
from app.models.user import User
from app.services.export_service import ExportService

router = APIRouter(prefix="/api/meetings", tags=["exports"])


@router.get("/{meeting_id}/export")
def export_meeting(
    meeting_id: int,
    format: str = Query("md", pattern="^(txt|md|json|docx|pdf)$"),
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> Response:
    try:
        document = ExportService(db).export(
            meeting_id,
            format,
            owner_id=user.id if user is not None else None,
        )
    except ValueError as exc:
        if str(exc) == "Meeting not found":
            raise HTTPException(status_code=404, detail="Meeting not found") from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    filename = quote(document.filename)
    return Response(
        content=document.content,
        media_type=document.media_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
