from enum import Enum
from typing import Any, Dict
import logging


class MessageType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"

class MessageCode(Enum):
    # Authentication
    AUTH_LOGIN_SUCCESS = "AUTH_001"
    AUTH_LOGIN_FAILED = "AUTH_002"
    AUTH_REGISTER_SUCCESS = "AUTH_003"
    AUTH_REGISTER_FAILED = "AUTH_004"
    AUTH_EMAIL_VERIFIED = "AUTH_005"
    AUTH_EMAIL_VERIFICATION_FAILED = "AUTH_006"
    AUTH_INVALID_CREDENTIALS = "AUTH_007"
    AUTH_ACCOUNT_INACTIVE = "AUTH_008"
    AUTH_EMAIL_EXISTS = "AUTH_009"
    AUTH_INVALID_TOKEN = "AUTH_010"
    AUTH_MFA_REQUIRED = "AUTH_011"
    AUTH_MFA_INVALID = "AUTH_012"
    
    # User Management
    USER_CREATED = "USER_001"
    USER_UPDATED = "USER_002"
    USER_DELETED = "USER_003"
    USER_NOT_FOUND = "USER_004"
    USER_ALREADY_EXISTS = "USER_005"
    
    # Customer Management
    CUSTOMER_CREATED = "CUST_001"
    CUSTOMER_UPDATED = "CUST_002"
    CUSTOMER_DELETED = "CUST_003"
    CUSTOMER_NOT_FOUND = "CUST_004"
    
    # Validation
    VALIDATION_ERROR = "VAL_001"
    INVALID_INPUT = "VAL_002"
    REQUIRED_FIELD = "VAL_003"
    
    # System
    SYSTEM_ERROR = "SYS_001"
    DATABASE_ERROR = "SYS_002"
    EXTERNAL_SERVICE_ERROR = "SYS_003"
    RATE_LIMIT_EXCEEDED = "SYS_004"

class Messages:
    """Centralized message store with templating support."""
    
    _messages: Dict[MessageCode, Dict[str, Any]] = {
        # Authentication Messages
        MessageCode.AUTH_LOGIN_SUCCESS: {
            "type": MessageType.SUCCESS,
            "message": "Login successful",
            "details": "User authenticated successfully"
        },
        MessageCode.AUTH_LOGIN_FAILED: {
            "type": MessageType.ERROR,
            "message": "Login failed",
            "details": "Invalid credentials provided"
        },
        MessageCode.AUTH_REGISTER_SUCCESS: {
            "type": MessageType.SUCCESS,
            "message": "Registration successful",
            "details": "Account created successfully. Please verify your email."
        },
        MessageCode.AUTH_REGISTER_FAILED: {
            "type": MessageType.ERROR,
            "message": "Registration failed",
            "details": "Unable to create account. Please try again."
        },
        MessageCode.AUTH_EMAIL_VERIFIED: {
            "type": MessageType.SUCCESS,
            "message": "Email verified",
            "details": "Your email has been verified successfully"
        },
        MessageCode.AUTH_EMAIL_VERIFICATION_FAILED: {
            "type": MessageType.ERROR,
            "message": "Email verification failed",
            "details": "Invalid or expired verification token"
        },
        MessageCode.AUTH_INVALID_CREDENTIALS: {
            "type": MessageType.ERROR,
            "message": "Invalid credentials",
            "details": "The provided credentials are invalid"
        },
        MessageCode.AUTH_ACCOUNT_INACTIVE: {
            "type": MessageType.ERROR,
            "message": "Account inactive",
            "details": "Please verify your email to activate your account"
        },
        MessageCode.AUTH_EMAIL_EXISTS: {
            "type": MessageType.ERROR,
            "message": "Email already registered",
            "details": "An account with this email already exists"
        },
        MessageCode.AUTH_INVALID_TOKEN: {
            "type": MessageType.ERROR,
            "message": "Invalid token",
            "details": "The provided token is invalid or expired"
        },
        MessageCode.AUTH_MFA_REQUIRED: {
            "type": MessageType.INFO,
            "message": "MFA required",
            "details": "Please enter the verification code sent to your device"
        },
        MessageCode.AUTH_MFA_INVALID: {
            "type": MessageType.ERROR,
            "message": "Invalid MFA code",
            "details": "The provided verification code is invalid"
        },
        
        # User Management Messages
        MessageCode.USER_CREATED: {
            "type": MessageType.SUCCESS,
            "message": "User created",
            "details": "User account created successfully"
        },
        MessageCode.USER_UPDATED: {
            "type": MessageType.SUCCESS,
            "message": "User updated",
            "details": "User information updated successfully"
        },
        MessageCode.USER_DELETED: {
            "type": MessageType.SUCCESS,
            "message": "User deleted",
            "details": "User account deleted successfully"
        },
        MessageCode.USER_NOT_FOUND: {
            "type": MessageType.ERROR,
            "message": "User not found",
            "details": "The requested user does not exist"
        },
        MessageCode.USER_ALREADY_EXISTS: {
            "type": MessageType.ERROR,
            "message": "User exists",
            "details": "A user with these details already exists"
        },
        
        # Customer Management Messages
        MessageCode.CUSTOMER_CREATED: {
            "type": MessageType.SUCCESS,
            "message": "Customer created",
            "details": "Customer account created successfully"
        },
        MessageCode.CUSTOMER_UPDATED: {
            "type": MessageType.SUCCESS,
            "message": "Customer updated",
            "details": "Customer information updated successfully"
        },
        MessageCode.CUSTOMER_DELETED: {
            "type": MessageType.SUCCESS,
            "message": "Customer deleted",
            "details": "Customer account deleted successfully"
        },
        MessageCode.CUSTOMER_NOT_FOUND: {
            "type": MessageType.ERROR,
            "message": "Customer not found",
            "details": "The requested customer does not exist"
        },
        
        # Validation Messages
        MessageCode.VALIDATION_ERROR: {
            "type": MessageType.ERROR,
            "message": "Validation error",
            "details": "The provided data is invalid"
        },
        MessageCode.INVALID_INPUT: {
            "type": MessageType.ERROR,
            "message": "Invalid input",
            "details": "The provided input is not valid"
        },
        MessageCode.REQUIRED_FIELD: {
            "type": MessageType.ERROR,
            "message": "Required field",
            "details": "This field is required"
        },
        
        # System Messages
        MessageCode.SYSTEM_ERROR: {
            "type": MessageType.ERROR,
            "message": "System error",
            "details": "An unexpected error occurred"
        },
        MessageCode.DATABASE_ERROR: {
            "type": MessageType.ERROR,
            "message": "Database error",
            "details": "An error occurred while accessing the database"
        },
        MessageCode.EXTERNAL_SERVICE_ERROR: {
            "type": MessageType.ERROR,
            "message": "External service error",
            "details": "An error occurred while communicating with an external service"
        },
        MessageCode.RATE_LIMIT_EXCEEDED: {
            "type": MessageType.ERROR,
            "message": "Rate limit exceeded",
            "details": "Too many requests. Please try again later"
        }
    }

    @classmethod
    def get_message(cls, code: MessageCode, **kwargs) -> Dict[str, Any]:
        """
        Get a message by its code and format it with any provided kwargs.
        
        Args:
            code: The message code to retrieve
            **kwargs: Optional parameters to format the message
            
        Returns:
            Dict containing the message details
        """
        if code not in cls._messages:
            raise ValueError(f"Unknown message code: {code}")
            
        message = cls._messages[code].copy()
        
        # Format message and details with kwargs if provided
        if kwargs:
            try:
                message["message"] = message["message"].format(**kwargs)
                message["details"] = message["details"].format(**kwargs)
            except (KeyError, IndexError, ValueError) as e:
                logging.getLogger("app.core.messages").error(f"Message formatting failed for code {code}: {e}. kwargs: {kwargs}")
                # Option 1: Return unformatted message
                # pass
                # Option 2: Raise a descriptive exception
                # raise ValueError(f"Failed to format message for code {code}: {e}")
        
        return message

    @classmethod
    def format_message(cls, code: MessageCode, **kwargs) -> str:
        """
        Get a formatted message string by its code.
        
        Args:
            code: The message code to retrieve
            **kwargs: Optional parameters to format the message
            
        Returns:
            Formatted message string
        """
        message = cls.get_message(code, **kwargs)
        return f"{message['message']}: {message['details']}"

def get_message(code: str, **kwargs) -> str:
    """
    Get a message by its code and format it with the provided parameters.
    
    Args:
        code: The message code to retrieve
        **kwargs: Parameters to format the message with
        
    Returns:
        The formatted message string
    """
    return Messages.get_message(code, **kwargs)

__all__ = [
    'MessageType',
    'MessageCode',
    'Messages',
    'get_message'
] 