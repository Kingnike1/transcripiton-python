"""Public schemas for participant identity management."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ParticipantUpdate(BaseModel):
    display_name: Optional[str] = Field(default=None, max_length=255)
    confirmed: bool = False

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def confirmed_requires_name(self) -> "ParticipantUpdate":
        if self.confirmed and not self.display_name:
            raise ValueError("Confirmed participant requires a display name")
        return self


class ParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    speaker_label: str
    display_name: Optional[str]
    confirmed: bool
    created_at: datetime
    updated_at: datetime


class ParticipantListResponse(BaseModel):
    meeting_id: int
    participants: list[ParticipantResponse]
