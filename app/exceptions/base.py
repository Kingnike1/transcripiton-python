"""
Base exception classes for AMIP.
All custom exceptions inherit from AMIPError.
"""


class AMIPError(Exception):
    """Base exception for all AMIP errors.
    
    All custom exceptions inherit from this base class
    to allow consistent error handling.
    """
    
    def __init__(self, message: str, details: str = ""):
        """Initialize AMIP error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details
        super().__init__(self.message)
