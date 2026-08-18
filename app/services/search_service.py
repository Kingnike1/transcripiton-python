"""Cross-meeting textual search with ownership isolation."""

from dataclasses import dataclass

from sqlalchemy import String, cast, func, or_
from sqlalchemy.orm import Session

from app.models.audio import Audio
from app.models.meeting import Meeting
from app.models.transcription import Transcription


@dataclass(frozen=True)
class SearchResult:
    meeting_id: int
    title: str
    status: str
    matched_in: list[str]
    snippet: str | None
    score: float


class SearchService:
    """Search meeting metadata and transcript text without external indexes."""

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def normalize_query(query: str) -> str:
        normalized = " ".join(query.split()).strip()
        if len(normalized) < 2:
            raise ValueError("Search query must be at least 2 characters")
        if len(normalized) > 200:
            raise ValueError("Search query must be at most 200 characters")
        return normalized

    @staticmethod
    def _snippet(text: str | None, query: str, radius: int = 90) -> str | None:
        if not text:
            return None
        position = text.casefold().find(query.casefold())
        if position < 0:
            return text[: radius * 2].strip()
        start = max(0, position - radius)
        end = min(len(text), position + len(query) + radius)
        prefix = "…" if start else ""
        suffix = "…" if end < len(text) else ""
        return f"{prefix}{text[start:end].strip()}{suffix}"

    def search(
        self,
        query: str,
        *,
        owner_id: int | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[SearchResult], int]:
        term = self.normalize_query(query)
        pattern = f"%{term}%"

        db_query = (
            self.db.query(Meeting, Transcription)
            .outerjoin(Audio, (Audio.meeting_id == Meeting.id) & (Audio.deleted_at.is_(None)))
            .outerjoin(
                Transcription,
                (Transcription.audio_id == Audio.id) & (Transcription.deleted_at.is_(None)),
            )
            .filter(Meeting.deleted_at.is_(None))
        )
        if owner_id is not None:
            db_query = db_query.filter(Meeting.owner_id == owner_id)

        match_filter = or_(
            Meeting.title.ilike(pattern),
            func.coalesce(Meeting.description, "").ilike(pattern),
            func.coalesce(Transcription.text, "").ilike(pattern),
            cast(Meeting.id, String).ilike(pattern),
        )
        matched = db_query.filter(match_filter)
        total = matched.count()
        rows = matched.order_by(Meeting.updated_at.desc()).offset(skip).limit(limit).all()

        results: list[SearchResult] = []
        term_folded = term.casefold()
        for meeting, transcription in rows:
            fields: list[str] = []
            title_match = term_folded in meeting.title.casefold()
            description_match = bool(meeting.description and term_folded in meeting.description.casefold())
            transcript_match = bool(transcription and term_folded in transcription.text.casefold())
            if title_match:
                fields.append("title")
            if description_match:
                fields.append("description")
            if transcript_match:
                fields.append("transcription")

            snippet_source = transcription.text if transcript_match and transcription else meeting.description
            score = (3.0 if title_match else 0.0) + (2.0 if description_match else 0.0) + (1.0 if transcript_match else 0.0)
            results.append(
                SearchResult(
                    meeting_id=meeting.id,
                    title=meeting.title,
                    status=meeting.status,
                    matched_in=fields,
                    snippet=self._snippet(snippet_source, term),
                    score=score,
                )
            )
        results.sort(key=lambda item: item.score, reverse=True)
        return results, total
