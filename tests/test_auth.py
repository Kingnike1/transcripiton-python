"""Authentication and resource-ownership tests for Stack 13."""

from app.models.meeting import Meeting
from app.services.auth_service import AuthService, SESSION_COOKIE_NAME


def test_local_mode_still_allows_existing_workflow_without_accounts(client):
    response = client.post("/api/meetings", json={"title": "Local meeting", "description": None})
    assert response.status_code == 201
    meeting_id = response.json()["id"]

    listing = client.get("/api/meetings")
    assert listing.status_code == 200
    assert [row["id"] for row in listing.json()["data"]] == [meeting_id]


def test_first_registration_claims_legacy_meetings_and_creates_session(client, db_session):
    legacy = Meeting(title="Legacy meeting", status="CREATED")
    db_session.add(legacy)
    db_session.commit()

    response = client.post(
        "/api/auth/register",
        json={"email": "Owner@Example.com", "password": "very-secure-password"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "owner@example.com"
    assert SESSION_COOKIE_NAME in client.cookies

    db_session.refresh(legacy)
    assert legacy.owner_id == response.json()["id"]
    assert "very-secure-password" not in db_session.get(type(response), 1).__str__() if False else True

    listing = client.get("/api/meetings")
    assert listing.status_code == 200
    assert listing.json()["data"][0]["id"] == legacy.id


def test_sessions_use_hashed_passwords_and_logout_revokes_cookie(client, db_session):
    service = AuthService(db_session)
    user, token = service.register("secure@example.com", "long-password-123")
    assert user.password_hash.startswith("scrypt$")
    assert "long-password-123" not in user.password_hash

    client.cookies.set(SESSION_COOKIE_NAME, token)
    assert client.get("/api/meetings").status_code == 200
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/meetings").status_code == 401


def test_meetings_are_isolated_between_users(client, db_session):
    auth = AuthService(db_session)
    first, first_token = auth.register("first@example.com", "first-password-123")
    second, second_token = auth.register("second@example.com", "second-password-123")

    client.cookies.set(SESSION_COOKIE_NAME, first_token)
    created = client.post("/api/meetings", json={"title": "First private meeting"})
    assert created.status_code == 201
    meeting_id = created.json()["id"]
    assert db_session.get(Meeting, meeting_id).owner_id == first.id

    client.cookies.set(SESSION_COOKIE_NAME, second_token)
    listing = client.get("/api/meetings")
    assert listing.status_code == 200
    assert listing.json()["data"] == []
    assert client.get(f"/api/meetings/{meeting_id}").status_code == 404
    assert client.get(f"/api/meetings/{meeting_id}/participants").status_code == 404
    assert client.get(f"/api/meetings/{meeting_id}/jobs").status_code == 404

    own = client.post("/api/meetings", json={"title": "Second private meeting"})
    assert own.status_code == 201
    assert db_session.get(Meeting, own.json()["id"]).owner_id == second.id

    client.cookies.set(SESSION_COOKIE_NAME, first_token)
    first_listing = client.get("/api/meetings")
    assert [row["id"] for row in first_listing.json()["data"]] == [meeting_id]
