"""
Database session management.
Handles connection to SQLite database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.database.base import Base

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session.
    
    Yields:
        Session: Database session
        
    Example:
        @app.get("/meetings")
        def get_meetings(db: Session = Depends(get_db)):
            return db.query(Meeting).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables.
    
    Creates all tables defined in models that inherit from Base.
    Should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)


def reset_db():
    """Reset database by dropping all tables.
    
    WARNING: This will delete all data. Only use for testing.
    """
    Base.metadata.drop_all(bind=engine)
    init_db()
