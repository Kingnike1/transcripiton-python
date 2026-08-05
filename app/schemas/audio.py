"""Pydantic schemas for audio upload responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AudioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    filename: str
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    duration: Optional[int]
    created_at: datetime


class AudioUploadResponse(BaseModel):
    meeting_id: int
    audio: AudioResponse
    status: str
