"""Custom exceptions for the QByte GL Data Service."""
from fastapi import HTTPException
from typing import Any, Dict, Optional


class GLDataServiceException(Exception):
    """Base exception for GL Data Service."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DataGenerationError(GLDataServiceException):
    """Raised when data generation fails."""
    pass


class InvalidDateRangeError(GLDataServiceException):
    """Raised when invalid date range is provided."""
    pass


class StreamingError(GLDataServiceException):
    """Raised when streaming operations fail."""
    pass


class ConfigurationError(GLDataServiceException):
    """Raised when service configuration is invalid."""
    pass


def create_http_exception(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create a standardized HTTP exception."""
    content = {
        "error": message,
        "status_code": status_code
    }
    if details:
        content["details"] = details
    
    return HTTPException(status_code=status_code, detail=content)


def validation_error(message: str, field: Optional[str] = None) -> HTTPException:
    """Create a validation error (400)."""
    details = {"field": field} if field else None
    return create_http_exception(400, message, details)


def not_found_error(resource: str, identifier: str) -> HTTPException:
    """Create a not found error (404)."""
    return create_http_exception(
        404, 
        f"{resource} not found",
        {"identifier": identifier}
    )


def internal_server_error(message: str = "Internal server error") -> HTTPException:
    """Create an internal server error (500)."""
    return create_http_exception(500, message)
