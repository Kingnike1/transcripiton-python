"""Tests for Meeting API routes."""


class TestMeetingAPI:
    """Tests for Meeting API endpoints."""

    def test_create_meeting(self, client, sample_meeting):
        response = client.post("/api/meetings", json=sample_meeting)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_meeting["title"]
        assert data["description"] == sample_meeting["description"]
        assert "id" in data
        assert "created_at" in data
        assert "status" in data

    def test_create_meeting_invalid_title(self, client):
        response = client.post(
            "/api/meetings",
            json={"title": "Ab", "description": "Test"},
        )
        assert response.status_code == 422

    def test_list_meetings(self, client, sample_meeting):
        client.post("/api/meetings", json=sample_meeting)
        response = client.get("/api/meetings")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 1
        assert data["total"] == 1

    def test_get_meeting(self, client, sample_meeting):
        create_response = client.post("/api/meetings", json=sample_meeting)
        meeting_id = create_response.json()["id"]
        response = client.get(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == meeting_id
        assert data["title"] == sample_meeting["title"]

    def test_get_meeting_not_found(self, client):
        assert client.get("/api/meetings/999").status_code == 404

    def test_update_meeting(self, client, sample_meeting, sample_meeting_update):
        create_response = client.post("/api/meetings", json=sample_meeting)
        meeting_id = create_response.json()["id"]
        response = client.put(
            f"/api/meetings/{meeting_id}",
            json=sample_meeting_update,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_meeting_update["title"]
        assert data["description"] == sample_meeting_update["description"]

    def test_update_meeting_not_found(self, client, sample_meeting_update):
        response = client.put("/api/meetings/999", json=sample_meeting_update)
        assert response.status_code == 404

    def test_delete_meeting(self, client, sample_meeting):
        create_response = client.post("/api/meetings", json=sample_meeting)
        meeting_id = create_response.json()["id"]
        response = client.delete(f"/api/meetings/{meeting_id}")
        assert response.status_code == 204
        list_response = client.get("/api/meetings")
        assert len(list_response.json()["data"]) == 0

    def test_delete_meeting_not_found(self, client):
        assert client.delete("/api/meetings/999").status_code == 404

    def test_home_page(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "AMIP" in response.text

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
