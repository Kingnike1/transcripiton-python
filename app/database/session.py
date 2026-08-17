"""SQLAlchemy engine and request-scoped session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.database.base import Base

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine_kwargs: dict = {"pool_pre_ping": True}
if _is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update(
        pool_size=settings.database.DB_POOL_SIZE,
        max_overflow=settings.database.DB_MAX_OVERFLOW,
        pool_recycle=settings.database.DB_POOL_RECYCLE_SECONDS,
        connect_args={"connect_timeout": settings.database.DB_CONNECT_TIMEOUT_SECONDS},
    )

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield one request-scoped database session and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db() -> None:
    """Recreate the schema explicitly for development/test tooling only."""
    if settings.ENVIRONMENT not in {"development", "test"}:
        raise RuntimeError("reset_db is disabled outside development and test")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
