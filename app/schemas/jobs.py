"""Public schemas for persistent processing jobs."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ProcessingJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    meeting_id: int
    job_type: str
    status: str
    progress: int
    attempt: int
    max_attempts: int
    error_message: Optional[str]
    result: Optional[dict[str, Any]]
    available_at: datetime
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class ProcessingJobListResponse(BaseModel):
    meeting_id: int
    jobs: list[ProcessingJobResponse]
