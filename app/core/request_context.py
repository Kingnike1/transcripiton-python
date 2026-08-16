"""Request correlation helpers for HTTP responses and logs."""

from uuid import uuid4

from fastapi import FastAPI, Request

REQUEST_ID_HEADER = "X-Request-ID"


def get_request_id(request: Request) -> str:
    """Return the server-generated request ID attached by middleware."""
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        return str(request_id)

    # Handlers can be called directly in tests or unusual middleware ordering.
    request_id = str(uuid4())
    request.state.request_id = request_id
    return request_id


def register_request_id_middleware(app: FastAPI) -> None:
    """Generate one trusted correlation ID for every HTTP request."""

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request.state.request_id
        return response
