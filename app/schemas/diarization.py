"""Public schemas for speaker diarization."""

from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.participant import ParticipantResponse


class SpeakerSegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transcription_id: int
    speaker_label: str
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float]
    participant_name: Optional[str] = None
    participant_confirmed: bool = False


class DiarizationResponse(BaseModel):
    meeting_id: int
    num_speakers: int
    participants: list[ParticipantResponse]
    segments: list[SpeakerSegmentResponse]
