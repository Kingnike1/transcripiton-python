"""HTTP routes for meeting operations."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_meeting_service
from app.schemas.meeting import (
    MeetingCreate,
    MeetingListResponse,
    MeetingResponse,
    MeetingUpdate,
)
from app.services.meeting_service import MeetingService

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.get("", response_model=MeetingListResponse)
def list_meetings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for title/description"),
    service: MeetingService = Depends(get_meeting_service),
) -> MeetingListResponse:
    """List active meetings with optional search and pagination."""
    if search:
        meetings = service.search(search, skip=skip, limit=limit)
        total = service.count_search(search)
    else:
        meetings = service.get_all(skip=skip, limit=limit)
        total = service.count()

    return MeetingListResponse(
        data=[MeetingResponse.model_validate(meeting) for meeting in meetings],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: int,
    service: MeetingService = Depends(get_meeting_service),
):
    """Return one active meeting or 404."""
    meeting = service.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.post("", response_model=MeetingResponse, status_code=201)
def create_meeting(
    meeting: MeetingCreate,
    service: MeetingService = Depends(get_meeting_service),
):
    """Create a new meeting."""
    try:
        return service.create(meeting)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_meeting(
    meeting_id: int,
    meeting: MeetingUpdate,
    service: MeetingService = Depends(get_meeting_service),
):
    """Update an active meeting or 404."""
    updated_meeting = service.update(meeting_id, meeting)
    if not updated_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return updated_meeting


@router.delete("/{meeting_id}", status_code=204)
def delete_meeting(
    meeting_id: int,
    service: MeetingService = Depends(get_meeting_service),
) -> None:
    """Soft-delete an active meeting or 404."""
    if not service.delete(meeting_id):
        raise HTTPException(status_code=404, detail="Meeting not found")
