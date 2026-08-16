"""Security and contract tests for public error responses."""

import asyncio
import json
from uuid import UUID

from fastapi import Request

from app.core.handlers import database_exception_handler, generic_exception_handler
from app.exceptions.database import DatabaseError


def _request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("127.0.0.1", 1234),
            "scheme": "http",
        }
    )


def _body(response) -> dict:
    return json.loads(response.body.decode("utf-8"))


def test_every_http_response_has_server_generated_request_id(client):
    response = client.get("/health")

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]
    assert str(UUID(request_id)) == request_id


def test_http_404_uses_standard_error_envelope_and_matching_request_id(client):
    response = client.get("/api/meetings/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["status"] == "error"
    assert body["code"] == "NOT_FOUND"
    assert body["detail"] == "Meeting not found"
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert "details" not in body


def test_request_validation_does_not_echo_payload_or_pydantic_details(client):
    response = client.post("/api/meetings", json={"title": "x"})

    assert response.status_code == 422
    body = response.json()
    assert body == {
        "status": "error",
        "code": "REQUEST_VALIDATION_ERROR",
        "detail": "Request validation failed",
        "request_id": response.headers["X-Request-ID"],
    }


def test_generic_500_never_exposes_exception_string():
    request = _request()
    response = asyncio.run(
        generic_exception_handler(
            request,
            RuntimeError("postgres://user:secret@db/internal /srv/private/file.py"),
        )
    )
    body = _body(response)

    assert response.status_code == 500
    assert body["code"] == "INTERNAL_ERROR"
    assert body["detail"] == "An unexpected error occurred"
    assert "secret" not in response.body.decode("utf-8")
    assert "/srv/private" not in response.body.decode("utf-8")
    assert "details" not in body
    UUID(body["request_id"])


def test_database_500_keeps_internal_details_out_of_public_response():
    request = _request()
    response = asyncio.run(
        database_exception_handler(
            request,
            DatabaseError(
                "SQL execution failed",
                details="sqlite:///private/app.db SELECT * FROM users",
            ),
        )
    )
    body = _body(response)

    assert response.status_code == 500
    assert body["code"] == "DATABASE_ERROR"
    assert body["detail"] == "A database operation failed"
    assert "sqlite" not in response.body.decode("utf-8")
    assert "SELECT" not in response.body.decode("utf-8")
    assert "details" not in body
