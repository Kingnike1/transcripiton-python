"""
Tests for Meeting API routes.
"""

import pytest
from fastapi.testclient import TestClient


class TestMeetingAPI:
    """Tests for Meeting API endpoints."""
    
    def test_create_meeting(self, client, sample_meeting):
        """Test creating a meeting via API.
        
        Verifies that a POST request creates a meeting successfully.
        """
        # Act
        response = client.post("/api/meetings", json=sample_meeting)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_meeting["title"]
        assert data["description"] == sample_meeting["description"]
        assert "id" in data
        assert "created_at" in data
        assert "status" in data
    
    def test_create_meeting_invalid_title(self, client):
        """Test creating a meeting with invalid title.
        
        Verifies that a POST request with short title returns 422 (Unprocessable Entity).
        """
        # Arrange
        invalid_data = {"title": "Ab", "description": "Test"}
        
        # Act
        response = client.post("/api/meetings", json=invalid_data)
        
        # Assert
        assert response.status_code == 422
    
    def test_list_meetings(self, client, sample_meeting):
        """Test listing meetings via API.
        
        Verifies that a GET request returns meetings.
        """
        # Arrange
        client.post("/api/meetings", json=sample_meeting)
        
        # Act
        response = client.get("/api/meetings")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 1
        assert data["total"] == 1
    
    def test_get_meeting(self, client, sample_meeting):
        """Test getting a meeting by ID via API.
        
        Verifies that a GET request returns the correct meeting.
        """
        # Arrange
        create_response = client.post("/api/meetings", json=sample_meeting)
        meeting_id = create_response.json()["id"]
        
        # Act
        response = client.get(f"/api/meetings/{meeting_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == meeting_id
        assert data["title"] == sample_meeting["title"]
    
    def test_get_meeting_not_found(self, client):
        """Test getting a non-existent meeting via API.
        
        Verifies that a GET request for non-existent meeting returns 404.
        """
        # Act
        response = client.get("/api/meetings/999")
        
        # Assert
        assert response.status_code == 404
    
    def test_update_meeting(self, client, sample_meeting, sample_meeting_update):
        """Test updating a meeting via API.
        
        Verifies that a PUT request updates the meeting successfully.
        """
        # Arrange
        create_response = client.post("/api/meetings", json=sample_meeting)
        meeting_id = create_response.json()["id"]
        
        # Act
        response = client.put(f"/api/meetings/{meeting_id}", json=sample_meeting_update)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_meeting_update["title"]
        assert data["description"] == sample_meeting_update["description"]
    
    def test_update_meeting_not_found(self, client, sample_meeting_update):
        """Test updating a non-existent meeting via API.
        
        Verifies that a PUT request for non-existent meeting returns 404.
        """
        # Act
        response = client.put("/api/meetings/999", json=sample_meeting_update)
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_meeting(self, client, sample_meeting):
        """Test deleting a meeting via API.
        
        Verifies that a DELETE request soft deletes the meeting.
        """
        # Arrange
        create_response = client.post("/api/meetings", json=sample_meeting)
        meeting_id = create_response.json()["id"]
        
        # Act
        response = client.delete(f"/api/meetings/{meeting_id}")
        
        # Assert
        assert response.status_code == 204
        
        # Verify meeting is not in list
        list_response = client.get("/api/meetings")
        assert len(list_response.json()["data"]) == 0
    
    def test_delete_meeting_not_found(self, client):
        """Test deleting a non-existent meeting via API.
        
        Verifies that a DELETE request for non-existent meeting returns 404.
        """
        # Act
        response = client.delete("/api/meetings/999")
        
        # Assert
        assert response.status_code == 404
    
    def test_home_page(self, client):
        """Test home page returns 200.
        
        Verifies that the home page loads successfully.
        """
        # Act
        response = client.get("/")
        
        # Assert
        assert response.status_code == 200
        assert "AMIP" in response.text
    
    def test_health_check(self, client):
        """Test health check endpoint.
        
        Verifies that health check returns healthy status.
        """
        # Act
        response = client.get("/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
