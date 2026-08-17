"""Tests for the server-rendered Sprint 8 interface."""

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import get_meeting_service
from main import app


class FakeMeetingService:
    def __init__(self, meetings):
        self.meetings = meetings

    def get_all(self, skip=0, limit=100):
        return self.meetings[skip : skip + limit]

    def get_by_id(self, meeting_id):
        return next((meeting for meeting in self.meetings if meeting.id == meeting_id), None)


def meeting(meeting_id=1):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=meeting_id,
        title="Daily de produto",
        description="Planejamento da semana",
        status="AUDIO_UPLOADED",
        created_at=now,
        updated_at=now,
    )


def test_meetings_page_lists_existing_meetings():
    app.dependency_overrides[get_meeting_service] = lambda: FakeMeetingService([meeting()])
    try:
        response = TestClient(app).get("/meetings")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "Daily de produto" in response.text
    assert "Nova reunião" in response.text


def test_meeting_detail_renders_transcription_workflow():
    app.dependency_overrides[get_meeting_service] = lambda: FakeMeetingService([meeting()])
    try:
        response = TestClient(app).get("/meetings/1")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "Enviar áudio" in response.text
    assert "Iniciar transcrição" in response.text
    assert "Transcrição" in response.text


def test_meeting_detail_returns_404_for_unknown_meeting():
    app.dependency_overrides[get_meeting_service] = lambda: FakeMeetingService([])
    try:
        response = TestClient(app).get("/meetings/999")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 404
