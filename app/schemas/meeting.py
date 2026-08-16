"""Pydantic schemas for meeting requests and responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ProcessingStatus


class MeetingBase(BaseModel):
    """Fields shared by meeting create/read models."""

    title: str = Field(..., min_length=3, max_length=255, description="Meeting title")
    description: Optional[str] = Field(None, description="Meeting description")


class MeetingCreate(MeetingBase):
    """Payload for creating a meeting."""


class MeetingUpdate(BaseModel):
    """Payload for partially updating a meeting."""

    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None


class MeetingResponse(MeetingBase):
    """Public representation of a meeting."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str = ProcessingStatus.CREATED.value
    created_at: datetime
    updated_at: datetime


class MeetingListResponse(BaseModel):
    """Paginated list of meetings."""

    status: str = "success"
    data: List[MeetingResponse]
    total: int
    skip: int = 0
    limit: int = 10
