"""Tests for Stack 15 cross-meeting search."""

from app.models.audio import Audio
from app.models.meeting import Meeting
from app.models.transcription import Transcription
from app.models.user import User
from app.services.search_service import SearchService


def _meeting(db_session, *, owner_id, title, description=None):
    meeting = Meeting(owner_id=owner_id, title=title, description=description, status="COMPLETED")
    db_session.add(meeting)
    db_session.flush()
    return meeting


def _transcript(db_session, meeting, text):
    audio = Audio(meeting_id=meeting.id, filename="meeting.wav", file_path="/tmp/meeting.wav")
    db_session.add(audio)
    db_session.flush()
    transcription = Transcription(audio_id=audio.id, text=text, language="pt")
    db_session.add(transcription)
    db_session.commit()


def test_search_matches_metadata_and_transcription(db_session):
    meeting = _meeting(db_session, owner_id=None, title="Planejamento trimestral", description="Produto e vendas")
    _transcript(db_session, meeting, "A equipe decidiu lançar o projeto Atlas em setembro.")

    results, total = SearchService(db_session).search("Atlas")

    assert total == 1
    assert results[0].meeting_id == meeting.id
    assert "transcription" in results[0].matched_in
    assert "Atlas" in (results[0].snippet or "")


def test_search_respects_owner_isolation(db_session):
    first = User(email="first@example.com", password_hash="hash")
    second = User(email="second@example.com", password_hash="hash")
    db_session.add_all([first, second])
    db_session.flush()
    visible = _meeting(db_session, owner_id=first.id, title="Projeto Orion")
    hidden = _meeting(db_session, owner_id=second.id, title="Projeto Orion secreto")
    db_session.commit()

    results, total = SearchService(db_session).search("Orion", owner_id=first.id)

    assert total == 1
    assert [item.meeting_id for item in results] == [visible.id]
    assert hidden.id not in [item.meeting_id for item in results]


def test_search_rejects_too_short_query(db_session):
    service = SearchService(db_session)
    try:
        service.search("x")
    except ValueError as exc:
        assert "at least 2" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_search_api_returns_results(client):
    created = client.post("/api/meetings", json={"title": "Reunião comercial", "description": "Negociação ACME"})
    assert created.status_code == 201

    response = client.get("/api/search", params={"q": "ACME"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["data"][0]["title"] == "Reunião comercial"
