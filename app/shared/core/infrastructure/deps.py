"""
Dependency injection utilities.
"""

from typing import TYPE_CHECKING, Optional, Generator, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.shared.core.exceptions import AuthenticationException
from app.shared.core.security.auth_core import decode_token, oauth2_scheme
from app.shared.core.security.roles import Role
from app.shared.db.session import get_db

if TYPE_CHECKING:
    from app.shared.models.user import User
    from app.shared.models.customer import Customer

def get_db_session() -> Generator[Session, None, None]:
    """
    Get database session.
    """
    return get_db()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session)
) -> "User":
    """
    Get current user from JWT token.
    """
    from app.shared.models.user import User
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except AuthenticationException:
        raise credentials_exception
    
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: "User" = Depends(get_current_user)
) -> "User":
    """
    Get current active user.
    
    Args:
        current_user: Current user from token
        
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

def get_current_superuser(
    current_user: "User" = Depends(get_current_active_user)
) -> "User":
    """
    Get current superuser.
    
    Args:
        current_user: Current active user
        
    Returns:
        Current superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def get_current_customer(
    db: Session = Depends(get_db),
    current_user: "User" = Depends(get_current_active_user)
) -> "Customer":
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
    from app.shared.models.customer import Customer
    customer = db.query(Customer).filter_by(user_id=current_user.id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer

def get_current_active_customer(
    current_customer: "Customer" = Depends(get_current_customer)
) -> "Customer":
    """
    Get current active customer.
    
    Args:
        current_customer: Current customer
        
    Returns:
        Current active customer
        
    Raises:
        HTTPException: If customer is inactive
    """
    if not current_customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive customer"
        )
    return current_customer


def get_current_user_dep():
    """
    Get current user dependency.
    """
    return get_current_user

def get_current_active_user_dep():
    """
    Get current active user dependency.
    """
    return get_current_active_user

def get_current_superuser_dep():
    """
    Get current superuser dependency.
    """
    return get_current_superuser

def get_current_customer_dep():
    """
    Get current customer dependency.
    """
    return get_current_customer

__all__ = [
    'get_current_active_user',
    'get_current_superuser',
    'get_current_customer',
    'get_current_active_customer',
    'get_current_user_dep',
    'get_current_active_user_dep',
    'get_current_superuser_dep',
    'get_current_customer_dep'
] 