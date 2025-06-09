"""
Authentication utilities.
"""

from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.shared.core.config import settings
from app.shared.core.exceptions import AuthenticationException
from app.shared.core.infrastructure.database import get_db
from app.shared.core.security.password_utils import verify_password
from app.shared.core.security.roles import Role
from app.shared.models.customer import Customer
from sqlalchemy.orm import Session
from fastapi import Depends
from app.shared.models.user import User
from app.shared.db.session import get_db
from fastapi import HTTPException
from typing import Any
from sqlalchemy.orm import Session
from fastapi import Depends
from app.shared.models.user import User
from app.shared.db.session import get_db
from fastapi import HTTPException
from typing import Any

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from token.
    
    Args:
        token: JWT token
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        if not isinstance(payload, dict) or "sub" not in payload:
            raise credentials_exception
        user_id: str = payload["sub"]
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current superuser.
    
    Args:
        current_user: Current active user
        
    Returns:
        Current superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if current_user.role != Role.SUPERUSER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> Optional[Any]:
    """
    Authenticate a user with email and password.
    """
    # Use string reference to avoid circular import
    user = db.query("User").filter_by(email=email).first()
    if not user:
        raise AuthenticationException("User not found")
    if not verify_password(password, user.hashed_password):
        raise AuthenticationException("Invalid password")
    return user

def get_current_customer(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Customer:
    """
    Get current customer.
    
    Args:
        db: Database session
        current_user: Current active user
        
    Returns:
        Current customer
        
    Raises:
        HTTPException: If user is not associated with a customer
    """
    customer = db.query(Customer).filter_by(user_id=current_user.id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer 