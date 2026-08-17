"""Application service for persisted speaker diarization."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.enums import ProcessingStatus
from app.models.audio import Audio
from app.models.meeting import Meeting
from app.models.speaker import SpeakerSegment as SpeakerSegmentModel
from app.models.transcription import Transcription
from app.services.interfaces import DiarizationResult


class DiarizationService:
    """Persist diarization and reconcile speaker turns with transcript text."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_meeting(self, meeting_id: int) -> list[SpeakerSegmentModel]:
        stmt = (
            select(SpeakerSegmentModel)
            .join(Transcription, SpeakerSegmentModel.transcription_id == Transcription.id)
            .join(Audio, Transcription.audio_id == Audio.id)
            .where(Audio.meeting_id == meeting_id, Audio.deleted_at.is_(None))
            .order_by(SpeakerSegmentModel.start_time, SpeakerSegmentModel.id)
        )
        return list(self.session.scalars(stmt).all())

    def persist_result(
        self,
        meeting_id: int,
        transcription: Transcription,
        result: DiarizationResult,
    ) -> list[SpeakerSegmentModel]:
        meeting = self.session.get(Meeting, meeting_id)
        if meeting is None:
            raise ValueError("Meeting not found")
        if meeting.status != ProcessingStatus.DIARIZING.value:
            raise ValueError(f"Meeting is not diarizing: {meeting.status}")

        self.session.execute(
            delete(SpeakerSegmentModel).where(
                SpeakerSegmentModel.transcription_id == transcription.id
            )
        )
        persisted: list[SpeakerSegmentModel] = []
        transcript_segments = list(transcription.segments)
        for segment in result.segments or []:
            text_parts = [
                item.text
                for item in transcript_segments
                if item.end_time > segment.start_time and item.start_time < segment.end_time
            ]
            row = SpeakerSegmentModel(
                transcription_id=transcription.id,
                speaker_label=segment.speaker_label,
                start_time=segment.start_time,
                end_time=segment.end_time,
                text=" ".join(text_parts).strip(),
                confidence=segment.confidence,
            )
            self.session.add(row)
            persisted.append(row)

        if not meeting.transition_status(ProcessingStatus.DIARIZED):
            raise ValueError("Invalid transition to DIARIZED")
        self.session.commit()
        for row in persisted:
            self.session.refresh(row)
        return persisted
