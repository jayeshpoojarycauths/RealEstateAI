"""
Core exceptions module.
"""

import logging
from typing import Any, Dict, Optional
from enum import Enum

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

# Get logger directly
logger = logging.getLogger("app")

class CommunicationErrorType(Enum):
    """Types of communication errors."""
    EMAIL_FAILED = "email_failed"
    SMS_FAILED = "sms_failed"
    PUSH_FAILED = "push_failed"
    WEBHOOK_FAILED = "webhook_failed"
    API_FAILED = "api_failed"
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    INVALID_CREDENTIALS = "invalid_credentials"
    INVALID_RECIPIENT = "invalid_recipient"
    TEMPLATE_ERROR = "template_error"
    ATTACHMENT_ERROR = "attachment_error"

class BaseAPIException(HTTPException):
    """Base exception for all API errors."""
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class ValidationException(BaseAPIException):
    """Exception for validation errors."""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class AuthenticationException(BaseAPIException):
    """Exception for authentication errors."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )

class AuthorizationException(BaseAPIException):
    """Exception for authorization errors."""
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class PermissionDenied(AuthorizationException):
    """Exception for permission denied errors."""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(detail=detail)

class NotFoundException(BaseAPIException):
    """Exception for not found errors."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class ConflictException(BaseAPIException):
    """Exception for conflict errors."""
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )

class RateLimitException(BaseAPIException):
    """Exception for rate limit errors."""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )

class ServiceUnavailableException(BaseAPIException):
    """Exception for service unavailable errors."""
    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )

class ExternalServiceError(BaseAPIException):
    """Exception raised when an external service fails."""
    def __init__(
        self,
        detail: str = "External service error occurred",
        status_code: int = 503,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(detail=detail, status_code=status_code, headers=headers)

class ValidationError(Exception):
    """Raised when validation fails."""
    pass

class NotFoundError(Exception):
    """Raised when a requested resource is not found."""
    pass

class CommunicationException(BaseAPIException):
    """Exception for communication errors."""
    def __init__(
        self,
        error_type: CommunicationErrorType,
        detail: str,
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        headers: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.error_type = error_type
        self.context = context or {}
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )

class EmailException(CommunicationException):
    """Exception for email-specific errors."""
    def __init__(
        self,
        detail: str,
        error_type: CommunicationErrorType = CommunicationErrorType.EMAIL_FAILED,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            error_type=error_type,
            detail=detail,
            context=context
        )

class SMSException(CommunicationException):
    """Exception for SMS-specific errors."""
    def __init__(
        self,
        detail: str,
        error_type: CommunicationErrorType = CommunicationErrorType.SMS_FAILED,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            error_type=error_type,
            detail=detail,
            context=context
        )

class PushNotificationException(CommunicationException):
    """Exception for push notification errors."""
    def __init__(
        self,
        detail: str,
        error_type: CommunicationErrorType = CommunicationErrorType.PUSH_FAILED,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            error_type=error_type,
            detail=detail,
            context=context
        )

class WebhookException(CommunicationException):
    """Exception for webhook errors."""
    def __init__(
        self,
        detail: str,
        error_type: CommunicationErrorType = CommunicationErrorType.WEBHOOK_FAILED,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            error_type=error_type,
            detail=detail,
            context=context
        )

def register_exception_handlers(app: FastAPI):
    """Register global exception handlers with the FastAPI app."""
    logger = logging.getLogger("uvicorn.error")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTPException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(CommunicationException)
    async def communication_exception_handler(request: Request, exc: CommunicationException):
        logger.error(
            f"Communication Error: {exc.error_type.value} - {exc.detail}",
            extra={"context": exc.context}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_type": exc.error_type.value,
                "context": exc.context
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )

__all__ = [
    'BaseAPIException',
    'ValidationException',
    'AuthenticationException',
    'AuthorizationException',
    'PermissionDenied',
    'NotFoundException',
    'ConflictException',
    'RateLimitException',
    'ServiceUnavailableException',
    'ExternalServiceError',
    'CommunicationException',
    'EmailException',
    'SMSException',
    'PushNotificationException',
    'WebhookException',
    'CommunicationErrorType'
] 