"""
Meeting Pydantic schemas.
Used for request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.core.enums import ProcessingStatus


class MeetingBase(BaseModel):
    """Base meeting schema with common fields.
    
    Attributes:
        title: Meeting title (3-255 characters)
        description: Optional meeting description
    """
    title: str = Field(..., min_length=3, max_length=255, description="Meeting title")
    description: Optional[str] = Field(None, description="Meeting description")


class MeetingCreate(MeetingBase):
    """Schema for creating a new meeting."""
    pass


class MeetingUpdate(BaseModel):
    """Schema for updating an existing meeting.
    
    All fields are optional for partial updates.
    """
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None


class MeetingResponse(MeetingBase):
    """Schema for meeting response.
    
    Includes all meeting fields including timestamps and status.
    
    Attributes:
        id: Meeting ID
        status: Current processing status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: int
    status: str = ProcessingStatus.CREATED.value
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MeetingListResponse(BaseModel):
    """Schema for meeting list response.
    
    Attributes:
        status: Response status
        data: List of meetings
        total: Total number of meetings
        skip: Number of records skipped
        limit: Limit used
    """
    status: str = "success"
    data: List[MeetingResponse]
    total: int
    skip: int = 0
    limit: int = 10
