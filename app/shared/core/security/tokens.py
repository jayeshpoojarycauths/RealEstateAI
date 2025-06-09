from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, TYPE_CHECKING

from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.shared.core.config import settings

if TYPE_CHECKING:
    from app.shared.models.user import User

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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )

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