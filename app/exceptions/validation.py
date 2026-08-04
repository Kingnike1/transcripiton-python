"""
Validation-related exceptions.
"""

from app.exceptions.base import AMIPError


class ValidationError(AMIPError):
    """Base exception for validation errors.
    
    Example:
        raise ValidationError("Invalid meeting title")
    """
    pass


class InvalidInputError(ValidationError):
    """Raised when input validation fails.
    
    Example:
        raise InvalidInputError("Meeting title cannot be empty")
    """
    pass


class InvalidConfigurationError(ValidationError):
    """Raised when configuration is invalid.
    
    Example:
        raise InvalidConfigurationError("DATABASE_URL not set")
    """
    pass
