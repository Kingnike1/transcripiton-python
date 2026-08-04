"""
Meeting API routes.
Handles HTTP requests for meeting operations.
All business logic is delegated to MeetingService.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_meeting_service
from app.schemas.meeting import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingListResponse,
)
from app.services.meeting_service import MeetingService

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.get("", response_model=MeetingListResponse)
def list_meetings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for title/description"),
    service: MeetingService = Depends(get_meeting_service),
):
    """List all meetings with optional search and pagination.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        search: Search term for title/description
        service: Meeting service dependency
        
    Returns:
        MeetingListResponse with meetings and metadata
    """
    if search:
        meetings = service.search(search, skip=skip, limit=limit)
        total = service.count_search(search)
    else:
        meetings = service.get_all(skip=skip, limit=limit)
        total = service.count()
    
    return MeetingListResponse(
        data=meetings,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: int,
    service: MeetingService = Depends(get_meeting_service),
):
    """Get a meeting by ID.
    
    Args:
        meeting_id: Meeting ID
        service: Meeting service dependency
        
    Returns:
        MeetingResponse with meeting details
        
    Raises:
        HTTPException: 404 if meeting not found
    """
    meeting = service.get_by_id(meeting_id)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return meeting


@router.post("", response_model=MeetingResponse, status_code=201)
def create_meeting(
    meeting: MeetingCreate,
    service: MeetingService = Depends(get_meeting_service),
):
    """Create a new meeting.
    
    Args:
        meeting: Meeting creation data
        service: Meeting service dependency
        
    Returns:
        MeetingResponse with created meeting
        
    Raises:
        HTTPException: 400 if title is invalid
    """
    try:
        created_meeting = service.create(meeting)
        return created_meeting
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_meeting(
    meeting_id: int,
    meeting: MeetingUpdate,
    service: MeetingService = Depends(get_meeting_service),
):
    """Update an existing meeting.
    
    Args:
        meeting_id: Meeting ID to update
        meeting: Meeting update data
        service: Meeting service dependency
        
    Returns:
        MeetingResponse with updated meeting
        
    Raises:
        HTTPException: 404 if meeting not found
    """
    updated_meeting = service.update(meeting_id, meeting)
    
    if not updated_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return updated_meeting


@router.delete("/{meeting_id}", status_code=204)
def delete_meeting(
    meeting_id: int,
    service: MeetingService = Depends(get_meeting_service),
):
    """Soft delete a meeting.
    
    Args:
        meeting_id: Meeting ID to delete
        service: Meeting service dependency
        
    Raises:
        HTTPException: 404 if meeting not found
    """
    deleted = service.delete(meeting_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Meeting not found")
