"""Production infrastructure behavior tests."""

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.session import engine
from main import app


def test_readiness_reports_database_reachable(test_db):
    response = TestClient(app).get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["database"] == "reachable"


def test_engine_can_execute_health_query(test_db):
    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
