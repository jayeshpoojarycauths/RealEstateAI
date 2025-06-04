from datetime import datetime, timedelta
from typing import Any, Union, List, Optional, Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.shared.core.config import settings
from functools import wraps
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from app.shared.models.user import User
from app.shared.models.customer import Customer
from app.shared.core.security.password_utils import verify_password, get_password_hash
from app.shared.core.constants import ALGORITHM
from app.shared.api.deps import deps
from sqlalchemy.orm import Session
import uuid
import asyncio

# Import security functions from shared core
from app.shared.core.security import (
    create_access_token,
    verify_jwt_token
)

# Security constants
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
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
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
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
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

class UserRole:
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    VIEWER = "viewer"

def get_current_customer(
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
) -> Customer:
    """Get current customer from user."""
    customer = db.query(Customer).filter(Customer.id == current_user.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer

# Alias for backward compatibility
get_current_tenant = get_current_customer

def require_role(roles: List[str]):
    """Decorator to require specific role(s) for an endpoint."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            if current_user.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def admin_required():
    """Decorator to require admin role."""
    return require_role([UserRole.ADMIN])

def manager_required():
    """Decorator to require manager role."""
    return require_role([UserRole.ADMIN, UserRole.MANAGER])

def agent_required():
    """Decorator to require agent role."""
    return require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT])

def viewer_required():
    """Decorator to require viewer role."""
    return require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT, UserRole.VIEWER]) 