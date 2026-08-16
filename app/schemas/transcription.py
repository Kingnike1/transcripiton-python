"""Public schemas for persisted transcriptions."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TranscriptionSegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sequence: int
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float]


class TranscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    audio_id: int
    text: str
    language: Optional[str]
    created_at: datetime
    segments: list[TranscriptionSegmentResponse]
