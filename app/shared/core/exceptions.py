from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class BaseAPIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class AuthenticationError(BaseAPIException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationError(BaseAPIException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class ValidationError(BaseAPIException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class NotFoundError(BaseAPIException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class RateLimitError(BaseAPIException):
    def __init__(self, detail: str = "Too many requests"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )

class DatabaseError(BaseAPIException):
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class ExternalServiceError(BaseAPIException):
    def __init__(self, detail: str = "External service error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        ) 