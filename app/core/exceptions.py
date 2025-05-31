from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class BaseAppException(Exception):
    """Base exception for all application errors."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(BaseAppException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)

class AuthorizationError(BaseAppException):
    """Raised when user lacks required permissions."""
    def __init__(self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)

class ValidationError(BaseAppException):
    """Raised when data validation fails."""
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)

class NotFoundError(BaseAppException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)

class ConflictError(BaseAppException):
    """Raised when there's a conflict with existing data."""
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_409_CONFLICT, details)

class RateLimitError(BaseAppException):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS, details)

class ExternalServiceError(BaseAppException):
    """Raised when an external service call fails."""
    def __init__(self, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY, details)

class DatabaseError(BaseAppException):
    """Raised when a database operation fails."""
    def __init__(self, message: str = "Database error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

class SMSError(ExternalServiceError):
    """Raised when SMS sending fails."""
    def __init__(self, message: str = "SMS sending failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY, details)

class EmailError(ExternalServiceError):
    """Raised when email sending fails."""
    def __init__(self, message: str = "Email sending failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY, details)

class ConfigurationError(BaseAppException):
    """Raised when there's a configuration issue."""
    def __init__(self, message: str = "Configuration error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

class BusinessLogicError(BaseAppException):
    """Raised when business logic validation fails."""
    def __init__(self, message: str = "Business logic error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details) 