"""HTTP routes for meeting operations."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_user_optional, get_meeting_service
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingListResponse, MeetingResponse, MeetingUpdate
from app.services.meeting_service import MeetingService

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


def _owner_id(user: User | None) -> int | None:
    return user.id if user is not None else None


@router.get("", response_model=MeetingListResponse)
def list_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    user: User | None = Depends(get_current_user_optional),
    service: MeetingService = Depends(get_meeting_service),
) -> MeetingListResponse:
    owner_id = _owner_id(user)
    if search:
        meetings = service.search(search, skip=skip, limit=limit, owner_id=owner_id)
        total = service.count_search(search, owner_id=owner_id)
    else:
        meetings = service.get_all(skip=skip, limit=limit, owner_id=owner_id)
        total = service.count(owner_id=owner_id)
    return MeetingListResponse(
        data=[MeetingResponse.model_validate(meeting) for meeting in meetings],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: int,
    user: User | None = Depends(get_current_user_optional),
    service: MeetingService = Depends(get_meeting_service),
):
    meeting = service.get_by_id(meeting_id, owner_id=_owner_id(user))
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.post("", response_model=MeetingResponse, status_code=201)
def create_meeting(
    meeting: MeetingCreate,
    user: User | None = Depends(get_current_user_optional),
    service: MeetingService = Depends(get_meeting_service),
):
    try:
        return service.create(meeting, owner_id=_owner_id(user))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_meeting(
    meeting_id: int,
    meeting: MeetingUpdate,
    user: User | None = Depends(get_current_user_optional),
    service: MeetingService = Depends(get_meeting_service),
):
    updated = service.update(meeting_id, meeting, owner_id=_owner_id(user))
    if not updated:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return updated


@router.delete("/{meeting_id}", status_code=204)
def delete_meeting(
    meeting_id: int,
    user: User | None = Depends(get_current_user_optional),
    service: MeetingService = Depends(get_meeting_service),
) -> None:
    if not service.delete(meeting_id, owner_id=_owner_id(user)):
        raise HTTPException(status_code=404, detail="Meeting not found")
