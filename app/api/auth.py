"""Authentication HTTP API."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.schemas.auth import AuthStatusResponse, LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import AuthService, SESSION_COOKIE_NAME, SESSION_DAYS

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.ENVIRONMENT in {"staging", "production"},
        samesite="lax",
        path="/",
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> UserResponse:
    service = AuthService(db)
    try:
        user, token = service.register(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _set_session_cookie(response, token)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=UserResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> UserResponse:
    result = AuthService(db).login(payload.email, payload.password)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user, token = result
    _set_session_cookie(response, token)
    return UserResponse.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> None:
    AuthService(db).logout(request.cookies.get(SESSION_COOKIE_NAME))
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


@router.get("/status", response_model=AuthStatusResponse)
def auth_status(request: Request, db: Session = Depends(get_db)) -> AuthStatusResponse:
    service = AuthService(db)
    enabled = service.authentication_enabled()
    user = service.user_from_token(request.cookies.get(SESSION_COOKIE_NAME)) if enabled else None
    return AuthStatusResponse(
        authentication_enabled=enabled,
        user=UserResponse.model_validate(user) if user is not None else None,
    )
