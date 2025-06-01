from typing import Any, Dict, Optional, List
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from .messages import MessageCode, Messages

class BaseAppException(Exception):
    """Base exception class for the application."""
    
    def __init__(
        self,
        message_code: MessageCode,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[str] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        self.message_code = message_code
        self.status_code = status_code
        self.details = details
        self.errors = errors or []
        self.kwargs = kwargs
        message = Messages.get_message(message_code, **kwargs)
        super().__init__(message["message"])

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        return {
            "code": self.message_code.value,
            "message": str(self),
            "details": self.details,
            "errors": self.errors,
            **self.kwargs
        }

class BusinessLogicException(BaseAppException):
    """Exception for business logic violations."""
    def __init__(
        self,
        message_code: MessageCode,
        details: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message_code=message_code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
            **kwargs
        )

# Authentication Exceptions
class AuthenticationException(BaseAppException):
    """Base class for authentication failures."""
    def __init__(
        self,
        message_code: MessageCode,
        details: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message_code=message_code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
            **kwargs
        )

class InvalidCredentialsException(AuthenticationException):
    """Exception for invalid credentials."""
    def __init__(self, **kwargs):
        super().__init__(
            message_code=MessageCode.AUTH_INVALID_CREDENTIALS,
            **kwargs
        )

class TokenExpiredException(AuthenticationException):
    """Exception for expired tokens."""
    def __init__(self, **kwargs):
        super().__init__(
            message_code=MessageCode.AUTH_INVALID_TOKEN,
            details="Token has expired",
            **kwargs
        )

class MFARequiredException(AuthenticationException):
    """Exception when MFA is required."""
    def __init__(self, **kwargs):
        super().__init__(
            message_code=MessageCode.AUTH_MFA_REQUIRED,
            **kwargs
        )

# Authorization Exceptions
class AuthorizationException(BaseAppException):
    """Base class for authorization failures."""
    def __init__(
        self,
        message_code: MessageCode,
        details: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message_code=message_code,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
            **kwargs
        )

class InsufficientPermissionsException(AuthorizationException):
    """Exception for insufficient permissions."""
    def __init__(self, required_permissions: List[str], **kwargs):
        super().__init__(
            message_code=MessageCode.AUTH_INSUFFICIENT_PERMISSIONS,
            details=f"Required permissions: {', '.join(required_permissions)}",
            required_permissions=required_permissions,
            **kwargs
        )

# Resource Exceptions
class ResourceNotFoundException(BaseAppException):
    """Base class for resource not found errors."""
    def __init__(
        self,
        message_code: MessageCode,
        resource_type: str,
        resource_id: Any,
        **kwargs
    ):
        super().__init__(
            message_code=message_code,
            status_code=status.HTTP_404_NOT_FOUND,
            details=f"{resource_type} with id {resource_id} not found",
            resource_type=resource_type,
            resource_id=resource_id,
            **kwargs
        )

class UserNotFoundException(ResourceNotFoundException):
    """Exception for user not found."""
    def __init__(self, user_id: Any, **kwargs):
        super().__init__(
            message_code=MessageCode.USER_NOT_FOUND,
            resource_type="User",
            resource_id=user_id,
            **kwargs
        )

class CustomerNotFoundException(ResourceNotFoundException):
    """Exception for customer not found."""
    def __init__(self, customer_id: Any, **kwargs):
        super().__init__(
            message_code=MessageCode.CUSTOMER_NOT_FOUND,
            resource_type="Customer",
            resource_id=customer_id,
            **kwargs
        )

# Validation Exceptions
class ValidationException(BaseAppException):
    """Base class for validation failures."""
    def __init__(
        self,
        message_code: MessageCode,
        errors: List[Dict[str, Any]],
        **kwargs
    ):
        super().__init__(
            message_code=message_code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=errors,
            **kwargs
        )

class SchemaValidationException(ValidationException):
    """Exception for schema validation failures."""
    def __init__(self, errors: List[Dict[str, Any]], **kwargs):
        super().__init__(
            message_code=MessageCode.VALIDATION_ERROR,
            errors=errors,
            **kwargs
        )

# Database Exceptions
class DatabaseException(BaseAppException):
    """Base class for database operation failures."""
    def __init__(
        self,
        message_code: MessageCode,
        details: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message_code=message_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            **kwargs
        )

class DuplicateEntryException(DatabaseException):
    """Exception for duplicate database entries."""
    def __init__(self, table: str, field: str, value: Any, **kwargs):
        super().__init__(
            message_code=MessageCode.DATABASE_ERROR,
            details=f"Duplicate entry in {table} for {field}={value}",
            table=table,
            field=field,
            value=value,
            **kwargs
        )

# External Service Exceptions
class ExternalServiceException(BaseAppException):
    """Base class for external service failures."""
    def __init__(
        self,
        message_code: MessageCode,
        service_name: str,
        details: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message_code=message_code,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details,
            service_name=service_name,
            **kwargs
        )

class ServiceUnavailableException(ExternalServiceException):
    """Exception for unavailable external services."""
    def __init__(self, service_name: str, **kwargs):
        super().__init__(
            message_code=MessageCode.EXTERNAL_SERVICE_ERROR,
            service_name=service_name,
            details=f"{service_name} is currently unavailable",
            **kwargs
        )

def get_error_response(
    request: Request,
    exc: Exception,
    status_code: int,
    message_code: MessageCode,
    details: Optional[str] = None,
    errors: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> JSONResponse:
    """
    Generate a standardized error response.
    
    Args:
        request: The FastAPI request object
        exc: The exception that was raised
        status_code: HTTP status code
        message_code: Message code for the error
        details: Optional additional details
        errors: Optional list of validation errors
        **kwargs: Additional parameters for message formatting
        
    Returns:
        JSONResponse with error details
    """
    message = Messages.get_message(message_code, **kwargs)
    
    error_response = {
        "status": "error",
        "code": message_code.value,
        "message": message["message"],
        "details": details or message["details"],
        "path": request.url.path,
        "method": request.method
    }
    if errors is not None:
        error_response["errors"] = errors
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )

async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """Global exception handler for custom application exceptions."""
    return get_error_response(
        request=request,
        exc=exc,
        status_code=exc.status_code,
        message_code=exc.message_code,
        details=exc.details,
        errors=exc.errors,
        **exc.kwargs
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Global exception handler for request validation errors."""
    errors = []
    for error in exc.errors():
        error_detail = {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        }
        if "ctx" in error:
            error_detail["ctx"] = error["ctx"]
        errors.append(error_detail)
    
    return get_error_response(
        request=request,
        exc=exc,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message_code=MessageCode.VALIDATION_ERROR,
        details=None,
        errors=errors
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions."""
    return get_error_response(
        request=request,
        exc=exc,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message_code=MessageCode.SYSTEM_ERROR,
        details=str(exc)
    )

def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    app.add_exception_handler(BaseAppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler) 