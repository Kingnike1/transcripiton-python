"""HTTP endpoints for meeting audio uploads and metadata."""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import get_audio_service, require_meeting_access
from app.exceptions.audio import (
    AudioAlreadyExistsError,
    AudioFormatError,
    AudioInspectorUnavailableError,
    AudioUploadError,
    MeetingNotFoundError,
)
from app.models.meeting import Meeting
from app.schemas.audio import AudioResponse, AudioUploadResponse
from app.services.audio_service import AudioService

router = APIRouter(prefix="/api/meetings", tags=["audio"])


@router.get("/{meeting_id}/audio/policy")
def get_audio_upload_policy(
    meeting_id: int,
    _meeting: Meeting = Depends(require_meeting_access),
    service: AudioService = Depends(get_audio_service),
) -> dict[str, object]:
    """Return safe upload constraints and whether replacement is currently allowed."""
    return service.upload_policy(meeting_id)


@router.post("/{meeting_id}/audio", response_model=AudioUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    meeting_id: int,
    file: UploadFile = File(...),
    replace: bool = Query(False),
    _meeting: Meeting = Depends(require_meeting_access),
    service: AudioService = Depends(get_audio_service),
) -> AudioUploadResponse:
    try:
        audio = await run_in_threadpool(
            service.upload_stream,
            meeting_id=meeting_id,
            filename=file.filename or "",
            content_type=file.content_type or "application/octet-stream",
            stream=file.file,
            replace_existing=replace,
        )
        return AudioUploadResponse(
            meeting_id=meeting_id,
            audio=AudioResponse.model_validate(audio),
            status="AUDIO_UPLOADED",
        )
    except MeetingNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except AudioAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=exc.message) from exc
    except AudioFormatError as exc:
        raise HTTPException(status_code=415, detail=exc.message) from exc
    except AudioUploadError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
    except AudioInspectorUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível inspecionar o áudio. Verifique o FFmpeg/FFprobe no diagnóstico.",
        ) from exc
    finally:
        await file.close()


@router.get("/{meeting_id}/audio", response_model=AudioResponse)
def get_audio_metadata(
    meeting_id: int,
    _meeting: Meeting = Depends(require_meeting_access),
    service: AudioService = Depends(get_audio_service),
) -> AudioResponse:
    try:
        audio = service.get_for_meeting(meeting_id)
    except MeetingNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    if audio is None:
        raise HTTPException(status_code=404, detail="Audio was not found")
    return AudioResponse.model_validate(audio)
