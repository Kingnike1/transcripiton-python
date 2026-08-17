"""Application service for persisted structured meeting intelligence."""

import json
from typing import Protocol

from sqlalchemy.orm import Session

from app.core.enums import ProcessingStatus
from app.models.analysis import MeetingAnalysis
from app.models.meeting import Meeting
from app.schemas.analysis import IntelligenceItem, MeetingAnalysisResponse, StructuredAnalysis
from app.services.diarization_service import DiarizationService
from app.services.participant_service import ParticipantService


class LLMProvider(Protocol):
    model: str

    def analyze(self, transcript: str) -> StructuredAnalysis: ...


class AnalysisService:
    """Build grounded LLM input, persist validated output and expose decoded results."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_meeting(self, meeting_id: int) -> MeetingAnalysis | None:
        return self.session.query(MeetingAnalysis).filter_by(meeting_id=meeting_id).one_or_none()

    def build_grounded_transcript(self, meeting_id: int) -> str:
        segments = DiarizationService(self.session).get_by_meeting(meeting_id)
        if not segments:
            raise ValueError("Meeting has no diarization")
        participants = {
            item.speaker_label: item
            for item in ParticipantService(self.session).list_by_meeting(meeting_id)
        }
        lines: list[str] = []
        for segment in segments:
            participant = participants.get(segment.speaker_label)
            name = (
                participant.display_name
                if participant and participant.confirmed and participant.display_name
                else segment.speaker_label
            )
            lines.append(
                f"[{segment.start_time:.2f}-{segment.end_time:.2f}] "
                f"{name} ({segment.speaker_label}): {segment.text}"
            )
        return "\n".join(lines)

    def analyze_and_persist(
        self,
        meeting_id: int,
        provider: LLMProvider,
        provider_name: str = "ollama",
    ) -> MeetingAnalysis:
        meeting = self.session.get(Meeting, meeting_id)
        if meeting is None:
            raise ValueError("Meeting not found")
        if meeting.status == ProcessingStatus.DIARIZED.value:
            if not meeting.transition_status(ProcessingStatus.SUMMARIZING):
                raise ValueError("Could not transition meeting to SUMMARIZING")
        elif meeting.status != ProcessingStatus.SUMMARIZING.value:
            raise ValueError(f"Meeting is not ready for analysis: {meeting.status}")

        grounded = self.build_grounded_transcript(meeting_id)
        result = provider.analyze(grounded)
        row = self.get_by_meeting(meeting_id) or MeetingAnalysis(meeting_id=meeting_id)
        row.summary = result.summary
        row.action_items = self._dump(result.action_items)
        row.decisions = self._dump(result.decisions)
        row.risks = self._dump(result.risks)
        row.open_questions = self._dump(result.open_questions)
        row.follow_up_tasks = self._dump(result.follow_up_tasks)
        row.provider = provider_name
        row.model_name = provider.model
        self.session.add(row)
        if not meeting.transition_status(ProcessingStatus.COMPLETED):
            raise ValueError("Could not transition meeting to COMPLETED")
        self.session.commit()
        self.session.refresh(row)
        return row

    def to_response(self, row: MeetingAnalysis) -> MeetingAnalysisResponse:
        return MeetingAnalysisResponse(
            meeting_id=row.meeting_id,
            summary=row.summary,
            action_items=self._load(row.action_items),
            decisions=self._load(row.decisions),
            risks=self._load(row.risks),
            open_questions=self._load(row.open_questions),
            follow_up_tasks=self._load(row.follow_up_tasks),
            provider=row.provider,
            model_name=row.model_name,
        )

    @staticmethod
    def _dump(items: list[IntelligenceItem]) -> str:
        return json.dumps([item.model_dump() for item in items], ensure_ascii=False)

    @staticmethod
    def _load(value: str | None) -> list[IntelligenceItem]:
        if not value:
            return []
        data = json.loads(value)
        return [IntelligenceItem.model_validate(item) for item in data]
