"""AMIP - AI Meeting Intelligence Platform main application."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.api.analysis import router as analysis_router
from app.api.audio import router as audio_router
from app.api.auth import router as auth_router
from app.api.diarization import router as diarization_router
from app.api.exports import router as exports_router
from app.api.jobs import router as jobs_router
from app.api.meetings import router as meetings_router
from app.api.onboarding import router as onboarding_router
from app.api.participants import router as participants_router
from app.api.readiness import router as readiness_router
from app.api.search import router as search_router
from app.api.transcriptions import router as transcriptions_router
from app.config import settings
from app.core.handlers import register_exception_handlers
from app.core.logging import logger
from app.core.request_context import register_request_id_middleware
from app.database.session import engine
from app.web import router as web_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting %s in %s environment", settings.APP_NAME, settings.ENVIRONMENT)
    try:
        yield
    finally:
        engine.dispose()
        logger.info("Stopped %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Meeting Intelligence Platform - Transcribe, analyze, and archive meetings",
    version="0.14.0",
    lifespan=lifespan,
)

register_request_id_middleware(app)
register_exception_handlers(app)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.include_router(auth_router)
app.include_router(meetings_router)
app.include_router(search_router)
app.include_router(exports_router)
app.include_router(audio_router)
app.include_router(jobs_router)
app.include_router(transcriptions_router)
app.include_router(diarization_router)
app.include_router(participants_router)
app.include_router(analysis_router)
app.include_router(readiness_router)
app.include_router(onboarding_router)
app.include_router(web_router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": app.version}


@app.get("/ready")
def readiness_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Readiness database check failed: %s", exc)
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ready", "database": "reachable", "version": app.version}


if __name__ == "__main__":
    logger.info("Starting %s on %s:%s", settings.APP_NAME, settings.HOST, settings.PORT)
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
