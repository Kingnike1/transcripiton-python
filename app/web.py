"""Server-rendered routes for the AMIP interface."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.dependencies import get_meeting_service
from app.database.session import get_db
from app.services.auth_service import AuthService, SESSION_COOKIE_NAME
from app.services.meeting_service import MeetingService
from app.services.search_service import SearchService

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="templates")


def _web_user(request: Request, db: Session):
    auth = AuthService(db)
    if not auth.authentication_enabled():
        return None
    return auth.user_from_token(request.cookies.get(SESSION_COOKIE_NAME))


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    auth = AuthService(db)
    user = auth.user_from_token(request.cookies.get(SESSION_COOKIE_NAME)) if auth.authentication_enabled() else None
    if user is not None:
        return RedirectResponse("/meetings", status_code=303)
    return templates.TemplateResponse(
        request,
        "auth.html",
        {"authentication_enabled": auth.authentication_enabled()},
    )


@router.get("/meetings", response_class=HTMLResponse)
def meetings_page(
    request: Request,
    q: str | None = Query(None, max_length=200),
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    user = _web_user(request, db)
    if AuthService(db).authentication_enabled() and user is None:
        return RedirectResponse("/login", status_code=303)
    owner_id = user.id if user is not None else None
    search_results = None
    search_error = None
    if q and q.strip():
        try:
            search_results, _ = SearchService(db).search(q, owner_id=owner_id, limit=100)
            meetings = []
        except ValueError as exc:
            search_error = str(exc)
            meetings = []
    else:
        meetings = service.get_all(skip=0, limit=100, owner_id=owner_id)
    return templates.TemplateResponse(
        request,
        "meetings.html",
        {
            "meetings": meetings,
            "current_user": user,
            "search_query": q or "",
            "search_results": search_results,
            "search_error": search_error,
        },
    )


@router.get("/meetings/{meeting_id}", response_class=HTMLResponse)
def meeting_detail_page(
    meeting_id: int,
    request: Request,
    db: Session = Depends(get_db),
    service: MeetingService = Depends(get_meeting_service),
):
    user = _web_user(request, db)
    if AuthService(db).authentication_enabled() and user is None:
        return RedirectResponse("/login", status_code=303)
    owner_id = user.id if user is not None else None
    meeting = service.get_by_id(meeting_id, owner_id=owner_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return templates.TemplateResponse(
        request,
        "meeting_detail.html",
        {"meeting": meeting, "current_user": user},
    )
