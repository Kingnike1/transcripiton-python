"""Application service for participant identity mapping."""

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.meeting import Meeting
from app.models.participant import Participant


class ParticipantService:
    """Manage the human identities associated with diarization speaker labels."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_meeting(self, meeting_id: int) -> list[Participant]:
        stmt = (
            select(Participant)
            .where(Participant.meeting_id == meeting_id)
            .order_by(Participant.speaker_label, Participant.id)
        )
        return list(self.session.scalars(stmt).all())

    def get_by_label(self, meeting_id: int, speaker_label: str) -> Participant | None:
        stmt = select(Participant).where(
            Participant.meeting_id == meeting_id,
            Participant.speaker_label == speaker_label,
        )
        return self.session.scalar(stmt)

    def ensure_labels(self, meeting_id: int, labels: Iterable[str]) -> list[Participant]:
        """Create placeholder identities for labels not seen in this meeting yet."""
        if self.session.get(Meeting, meeting_id) is None:
            raise ValueError("Meeting not found")

        normalized = sorted({label.strip() for label in labels if label and label.strip()})
        existing = {row.speaker_label: row for row in self.list_by_meeting(meeting_id)}
        changed = False
        for label in normalized:
            if label in existing:
                continue
            row = Participant(meeting_id=meeting_id, speaker_label=label)
            self.session.add(row)
            existing[label] = row
            changed = True

        if changed:
            self.session.flush()
        return [existing[label] for label in normalized]

    def update_identity(
        self,
        meeting_id: int,
        speaker_label: str,
        *,
        display_name: str | None,
        confirmed: bool,
    ) -> Participant:
        participant = self.get_by_label(meeting_id, speaker_label)
        if participant is None:
            raise LookupError("Participant not found")
        if confirmed and not display_name:
            raise ValueError("Confirmed participant requires a display name")

        participant.display_name = display_name.strip() if display_name else None
        participant.confirmed = confirmed
        self.session.commit()
        self.session.refresh(participant)
        return participant
