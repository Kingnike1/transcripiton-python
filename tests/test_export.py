"""Tests for Stack 16 meeting export."""

import json

from app.models.meeting import Meeting
from app.models.user import User
from app.services.export_service import ExportService


def _meeting(db_session, *, owner_id=None, title="Reunião de Produto"):
    meeting = Meeting(
        owner_id=owner_id,
        title=title,
        description="Planejamento do próximo ciclo",
        status="CREATED",
    )
    db_session.add(meeting)
    db_session.commit()
    db_session.refresh(meeting)
    return meeting


def test_export_incomplete_meeting_remains_valid(db_session):
    meeting = _meeting(db_session)
    service = ExportService(db_session)

    txt = service.export(meeting.id, "txt")
    markdown = service.export(meeting.id, "md")
    payload = json.loads(service.export(meeting.id, "json").content)

    assert txt.content.startswith(b"Reuni")
    assert "Transcrição ainda não disponível." in txt.content.decode("utf-8")
    assert markdown.media_type.startswith("text/markdown")
    assert payload["meeting_id"] == meeting.id
    assert payload["segments"] == []
    assert payload["analysis"] is None


def test_export_generates_docx_and_pdf(db_session):
    meeting = _meeting(db_session, title="Ata Executiva")
    service = ExportService(db_session)

    docx = service.export(meeting.id, "docx")
    pdf = service.export(meeting.id, "pdf")

    assert docx.content.startswith(b"PK")
    assert docx.filename.endswith(".docx")
    assert pdf.content.startswith(b"%PDF")
    assert pdf.filename.endswith(".pdf")


def test_export_respects_owner_isolation(db_session):
    owner = User(email="owner-export@example.com", password_hash="hash")
    outsider = User(email="outsider-export@example.com", password_hash="hash")
    db_session.add_all([owner, outsider])
    db_session.flush()
    meeting = _meeting(db_session, owner_id=owner.id)

    service = ExportService(db_session)
    assert service.export(meeting.id, "json", owner_id=owner.id).content

    try:
        service.export(meeting.id, "json", owner_id=outsider.id)
    except ValueError as exc:
        assert str(exc) == "Meeting not found"
    else:
        raise AssertionError("cross-owner export must be blocked")


def test_export_api_downloads_file(client):
    created = client.post(
        "/api/meetings",
        json={"title": "Ata do Conselho", "description": "Decisões do mês"},
    )
    assert created.status_code == 201
    meeting_id = created.json()["id"]

    response = client.get(f"/api/meetings/{meeting_id}/export", params={"format": "md"})

    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("attachment;")
    assert "# Ata do Conselho" in response.text


def test_export_api_rejects_unknown_format(client):
    created = client.post(
        "/api/meetings",
        json={"title": "Reunião válida", "description": None},
    )
    meeting_id = created.json()["id"]

    response = client.get(f"/api/meetings/{meeting_id}/export", params={"format": "exe"})

    assert response.status_code == 422
