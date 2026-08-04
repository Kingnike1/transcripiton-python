"""
AMIP - AI Meeting Intelligence Platform
Main application entry point.
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.api.meetings import router as meetings_router
from app.core.config import settings
from app.core.logging import logger
from app.database.session import init_db

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Meeting Intelligence Platform - Transcribe, analyze, and archive meetings",
    version="0.1.0",
)

# Initialize database
init_db()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(meetings_router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Home page.
    
    Returns:
        HTMLResponse with home page template
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    """Health check endpoint.
    
    Returns:
        Dictionary with application status
    """
    return {
        "status": "healthy",
        "version": app.version,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler.
    
    Args:
        request: HTTP request
        exc: Exception that occurred
        
    Returns:
        HTMLResponse with error page
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return HTMLResponse(
        content=f"<h1>500 - Internal Server Error</h1><p>{str(exc)}</p>",
        status_code=500,
    )


if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
