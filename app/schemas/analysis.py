"""Public schemas for structured meeting intelligence."""

from pydantic import BaseModel, ConfigDict, Field


class EvidenceRef(BaseModel):
    speaker_label: str | None = None
    participant_name: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    quote: str | None = None


class IntelligenceItem(BaseModel):
    text: str
    owner: str | None = None
    evidence: list[EvidenceRef] = Field(default_factory=list)


class StructuredAnalysis(BaseModel):
    summary: str
    action_items: list[IntelligenceItem] = Field(default_factory=list)
    decisions: list[IntelligenceItem] = Field(default_factory=list)
    risks: list[IntelligenceItem] = Field(default_factory=list)
    open_questions: list[IntelligenceItem] = Field(default_factory=list)
    follow_up_tasks: list[IntelligenceItem] = Field(default_factory=list)


class MeetingAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    meeting_id: int
    summary: str | None
    action_items: list[IntelligenceItem]
    decisions: list[IntelligenceItem]
    risks: list[IntelligenceItem]
    open_questions: list[IntelligenceItem]
    follow_up_tasks: list[IntelligenceItem]
    provider: str | None = None
    model_name: str | None = None
