"""
Core authentication logic.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import re

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.shared.core.config import settings
from app.shared.core.exceptions import AuthenticationException, ValidationError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def validate_subject(subject: str) -> None:
    """
    Validate token subject.
    
    Args:
        subject: Token subject to validate
        
    Raises:
        ValidationError: If subject is invalid
    """
    if not isinstance(subject, str):
        raise ValidationError("Subject must be a string")
    if not subject.strip():
        raise ValidationError("Subject cannot be empty")
    if not re.match(r'^[a-zA-Z0-9_-]+$', subject):
        raise ValidationError("Subject contains invalid characters")

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create access token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional expiration time delta
        
    Returns:
        JWT access token
        
    Raises:
        ValidationError: If subject is invalid
    """
    validate_subject(subject)
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": subject,
        "type": "access"
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create refresh token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional expiration time delta
        
    Returns:
        JWT refresh token
        
    Raises:
        ValidationError: If subject is invalid
    """
    validate_subject(subject)
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "exp": expire,
        "sub": subject,
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password.
    """
    return pwd_context.hash(password)

def decode_token(token: str) -> dict:
    """
    Decode a JWT token.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise AuthenticationException("Could not validate credentials") 