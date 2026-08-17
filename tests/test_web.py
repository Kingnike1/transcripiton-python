"""Tests for the server-rendered meeting interface."""

from app.models.meeting import Meeting


def _meeting(db_session, meeting_id: int = 1) -> Meeting:
    row = Meeting(
        id=meeting_id,
        title="Daily de produto",
        description="Planejamento da semana",
        status="AUDIO_UPLOADED",
    )
    db_session.add(row)
    db_session.commit()
    return row


def test_meetings_page_lists_existing_meetings(client, db_session):
    _meeting(db_session)
    response = client.get("/meetings")
    assert response.status_code == 200
    assert "Daily de produto" in response.text
    assert "Nova reunião" in response.text


def test_meeting_detail_renders_transcription_workflow(client, db_session):
    _meeting(db_session)
    response = client.get("/meetings/1")
    assert response.status_code == 200
    assert "Enviar áudio" in response.text
    assert "Iniciar transcrição" in response.text
    assert "Transcrição" in response.text


def test_meeting_detail_returns_404_for_unknown_meeting(client):
    response = client.get("/meetings/999")
    assert response.status_code == 404
