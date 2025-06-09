"""
Authentication utilities.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, TYPE_CHECKING

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.shared.core.config import settings
from app.shared.core.security.role_types import Role
from app.shared.db.session import get_db
from app.shared.core.security.tokens import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    verify_jwt_token
)
from app.shared.core.security.password_utils import verify_password, get_password_hash
from app.shared.core.exceptions import AuthenticationException, ValidationError

if TYPE_CHECKING:
    from app.shared.models.user import User
    from app.shared.models.customer import Customer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> "User":
    """Get current user from token."""
    from app.shared.models.user import User
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: "User" = Depends(get_current_user)
) -> "User":
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(
    current_user: "User" = Depends(get_current_user)
) -> "User":
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

async def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> Optional["User"]:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User's email
        password: User's password
        
    Returns:
        User if authentication successful, None otherwise
    """
    from app.shared.models.user import User
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_active_customer_with_custom_exception(
    current_customer: Optional["Customer"] = None
) -> "Customer":
    """Get current active customer with custom exception."""
    from app.shared.core.infrastructure.deps import get_current_customer
    if current_customer is None:
        current_customer = await get_current_customer()
    if not current_customer.is_active:
        raise AuthenticationException("Inactive customer")
    return current_customer

# Re-export commonly used dependencies
__all__ = [
    "authenticate_user",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "create_access_token",
    "create_refresh_token",
    "verify_password",
    "get_password_hash",
    "decode_access_token",
    "decode_refresh_token",
    "verify_jwt_token",
    "get_current_active_customer_with_custom_exception",
    "Role"
] 