"""
Test configuration and fixtures.
Provides common test utilities and fixtures.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.session import get_db
from main import app


# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create test session
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test.
    
    Yields:
        Session: Database session
        
    After test:
        Drops all tables and recreates them
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database session.
    
    Args:
        db_session: Database session fixture
        
    Yields:
        TestClient: FastAPI test client
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Remove override
    app.dependency_overrides.clear()


@pytest.fixture
def sample_meeting():
    """Create sample meeting data.
    
    Returns:
        dict: Meeting data
    """
    return {
        "title": "Test Meeting",
        "description": "This is a test meeting description",
    }


@pytest.fixture
def sample_meeting_update():
    """Create sample meeting update data.
    
    Returns:
        dict: Meeting update data
    """
    return {
        "title": "Updated Test Meeting",
        "description": "Updated description",
    }
