"""SQLAlchemy engine and request-scoped session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.database.base import Base

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
    if "sqlite" in settings.DATABASE_URL
    else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield one request-scoped database session and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db() -> None:
    """Recreate the schema explicitly for local/test tooling only.

    Production and normal application startup must use Alembic migrations and
    must never call this helper.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
