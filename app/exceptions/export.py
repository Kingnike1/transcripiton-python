"""
Export-related exceptions.
"""

from app.exceptions.base import AMIPError


class ExportError(AMIPError):
    """Base exception for export operation failures.
    
    Example:
        raise ExportError("Failed to generate PDF")
    """
    pass


class UnsupportedFormatError(ExportError):
    """Raised when export format is not supported.
    
    Example:
        raise UnsupportedFormatError("Format .xlsx is not supported")
    """
    pass


class ExportGenerationError(ExportError):
    """Raised when export generation fails.
    
    Example:
        raise ExportGenerationError("PDF generation failed: missing dependencies")
    """
    pass
