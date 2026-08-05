"""HTTP endpoints for meeting audio uploads and metadata."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import get_audio_service
from app.exceptions.audio import AudioAlreadyExistsError, MeetingNotFoundError
from app.schemas.audio import AudioResponse, AudioUploadResponse
from app.services.audio_service import AudioService

router = APIRouter(prefix="/api/meetings", tags=["audio"])


@router.post(
    "/{meeting_id}/audio",
    response_model=AudioUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_audio(
    meeting_id: int,
    file: UploadFile = File(...),
    service: AudioService = Depends(get_audio_service),
) -> AudioUploadResponse:
    try:
        content = await file.read()
        audio = service.upload(
            meeting_id=meeting_id,
            filename=file.filename or "",
            content_type=file.content_type or "application/octet-stream",
            content=content,
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
    finally:
        await file.close()


@router.get("/{meeting_id}/audio", response_model=AudioResponse)
def get_audio_metadata(
    meeting_id: int,
    service: AudioService = Depends(get_audio_service),
) -> AudioResponse:
    try:
        audio = service.get_for_meeting(meeting_id)
    except MeetingNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    if audio is None:
        raise HTTPException(status_code=404, detail="Audio was not found")
    return AudioResponse.model_validate(audio)
