"""Schemas for cross-meeting textual search."""

from pydantic import BaseModel, Field


class SearchHit(BaseModel):
    """One meeting matched by metadata or transcription content."""

    meeting_id: int
    title: str
    status: str
    matched_in: list[str] = Field(default_factory=list)
    snippet: str | None = None
    score: float = 0.0


class SearchResponse(BaseModel):
    """Paginated textual search response."""

    status: str = "success"
    query: str
    data: list[SearchHit]
    total: int
    skip: int = 0
    limit: int = 20
