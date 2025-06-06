from fastapi import HTTPException, status, FastAPI, Request
from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse
import logging

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
    'ExternalServiceError'
] 