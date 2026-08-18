"""HTTP endpoint for cross-meeting textual search."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_optional
from app.database.session import get_db
from app.models.user import User
from app.schemas.search import SearchHit, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search_meetings(
    q: str = Query(..., min_length=2, max_length=200),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> SearchResponse:
    service = SearchService(db)
    try:
        results, total = service.search(
            q,
            owner_id=user.id if user is not None else None,
            skip=skip,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SearchResponse(
        query=service.normalize_query(q),
        data=[SearchHit(**result.__dict__) for result in results],
        total=total,
        skip=skip,
        limit=limit,
    )
