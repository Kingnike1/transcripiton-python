"""Pydantic schemas for public audio responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AudioResponse(BaseModel):
    """Public audio metadata without internal filesystem/storage identifiers."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    filename: str
    file_size: Optional[int]
    mime_type: Optional[str]
    duration: Optional[int]
    codec_name: Optional[str]
    channels: Optional[int]
    sample_rate: Optional[int]
    created_at: datetime


class AudioUploadResponse(BaseModel):
    meeting_id: int
    audio: AudioResponse
    status: str
