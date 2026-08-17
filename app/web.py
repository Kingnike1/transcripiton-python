"""Server-rendered routes for the internal AMIP interface."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_meeting_service
from app.services.meeting_service import MeetingService

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="templates")


@router.get("/meetings", response_class=HTMLResponse)
def meetings_page(
    request: Request,
    service: MeetingService = Depends(get_meeting_service),
) -> HTMLResponse:
    """Render the meeting workspace."""
    meetings = service.get_all(skip=0, limit=100)
    return templates.TemplateResponse(
        request,
        "meetings.html",
        {"meetings": meetings},
    )


@router.get("/meetings/{meeting_id}", response_class=HTMLResponse)
def meeting_detail_page(
    meeting_id: int,
    request: Request,
    service: MeetingService = Depends(get_meeting_service),
) -> HTMLResponse:
    """Render one meeting and let the browser orchestrate the existing APIs."""
    meeting = service.get_by_id(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return templates.TemplateResponse(
        request,
        "meeting_detail.html",
        {"meeting": meeting},
    )
