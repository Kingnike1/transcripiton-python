"""AMIP - AI Meeting Intelligence Platform main application."""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.audio import router as audio_router
from app.api.meetings import router as meetings_router
from app.config import settings
from app.core.handlers import register_exception_handlers
from app.core.logging import logger
from app.database.session import init_db

app = FastAPI(
    title=settings.APP_NAME,
    description="AI Meeting Intelligence Platform - Transcribe, analyze, and archive meetings",
    version="0.2.0",
)

init_db()
register_exception_handlers(app)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.include_router(meetings_router)
app.include_router(audio_router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": app.version}


if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
