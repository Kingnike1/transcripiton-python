"""
Database-related exceptions.
"""

from app.exceptions.base import AMIPError


class DatabaseError(AMIPError):
    """Base exception for database errors.
    
    Example:
        raise DatabaseError("Database connection failed")
    """
    pass


class RecordNotFoundError(DatabaseError):
    """Raised when a database record is not found.
    
    Example:
        raise RecordNotFoundError("Meeting with ID 123 not found")
    """
    pass


class RecordAlreadyExistsError(DatabaseError):
    """Raised when attempting to create a duplicate record.
    
    Example:
        raise RecordAlreadyExistsError("Meeting with this title already exists")
    """
    pass
