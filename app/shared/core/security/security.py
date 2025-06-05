from datetime import datetime, timedelta
from typing import Any, Union, List, Optional, Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.shared.core.config import settings
from functools import wraps
from fastapi import HTTPException, Depends, status
from app.shared.models.user import User
from app.shared.models.customer import Customer
from app.shared.core.security.password_utils import verify_password, get_password_hash
from app.shared.core.constants import JWT_ALGORITHM
from sqlalchemy.orm import Session
import uuid
import asyncio
from app.shared.core.security.roles import Role
import pyotp
import hashlib
import base64
from cryptography.fernet import Fernet

# Security constants
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encrypt_value(value: str) -> str:
    """
    Encrypt a value using Fernet symmetric encryption.
    
    Args:
        value: The value to encrypt
        
    Returns:
        str: The encrypted value as a base64 string
    """
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt a value that was encrypted using encrypt_value.
    
    Args:
        encrypted_value: The encrypted value as a base64 string
        
    Returns:
        str: The decrypted value
    """
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    f = Fernet(key)
    return f.decrypt(encrypted_value.encode()).decode()

def hash_code(code: str) -> str:
    """
    Hash a code (e.g., backup code) using SHA-256.
    
    Args:
        code: The code to hash
        
    Returns:
        str: The hashed code
    """
    return hashlib.sha256(code.encode()).hexdigest()

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT access token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Dict containing the decoded token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Could not validate token: {str(e)}")

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional expiration time delta
        
    Returns:
        str: JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional expiration time delta
        
    Returns:
        str: JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def generate_verification_token(
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate an email verification token.
    
    Args:
        email: User's email address
        expires_delta: Optional expiration time delta
        
    Returns:
        str: JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)  # 24 hours by default
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "email_verification"
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def generate_password_reset_token(
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a password reset token.
    
    Args:
        email: User's email address
        expires_delta: Optional expiration time delta
        
    Returns:
        str: JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour by default
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "password_reset"
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def require_role(required_roles: list[Role]):
    """Dependency for requiring specific roles."""
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return dependency

# Export commonly used role-based dependencies
def require_admin():
    """Require admin role."""
    return require_role([Role.ADMIN])

def require_manager():
    """Require manager or admin role."""
    return require_role([Role.ADMIN, Role.MANAGER])

def require_agent():
    """Require agent, manager, or admin role."""
    return require_role([Role.ADMIN, Role.MANAGER, Role.AGENT])

def require_viewer():
    """Require viewer, agent, manager, or admin role."""
    return require_role([Role.ADMIN, Role.MANAGER, Role.AGENT, Role.VIEWER])

def decode_refresh_token(token: str) -> dict:
    """Decode and verify JWT refresh token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify a JWT token and return its payload.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        Dict containing the token payload
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

def verify_mfa_code(code: str, secret_key: str) -> bool:
    """
    Verify a TOTP (Time-based One-Time Password) code.
    
    Args:
        code: The MFA code to verify
        secret_key: The user's MFA secret key
        
    Returns:
        bool: True if the code is valid, False otherwise
    """
    try:
        totp = pyotp.TOTP(secret_key)
        return totp.verify(code)
    except Exception as e:
        logger.error(f"Error verifying MFA code: {str(e)}")
        return False

__all__ = [
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'create_refresh_token',
    'decode_access_token',
    'decode_refresh_token',
    'require_role',
    'require_admin',
    'require_manager',
    'require_agent',
    'require_viewer',
    'verify_jwt_token',
    'verify_mfa_code',
    'encrypt_value',
    'decrypt_value',
    'hash_code',
    'generate_verification_token',
    'generate_password_reset_token'
] 