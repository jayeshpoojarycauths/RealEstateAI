"""
Security dependencies for FastAPI endpoints.
"""

from typing import List, TYPE_CHECKING
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.shared.core.security.role_types import Role
from app.shared.core.infrastructure.deps import get_db
from app.shared.core.security.auth import (
    get_current_user,
    get_current_active_user,
    get_current_superuser
)

if TYPE_CHECKING:
    from app.shared.models.user import User

def require_role(allowed_roles: List[Role]):
    """
    Dependency to require specific roles.
    
    Args:
        allowed_roles: List of roles that are allowed to access the endpoint
        
    Returns:
        A dependency function that checks if the current user has one of the allowed roles
    """
    async def dependency(current_user: "User" = Depends(get_current_user)):
        if current_user.role not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return dependency

async def admin_required(current_user=Depends(get_current_user)):
    """
    Dependency to require admin role.
    
    Args:
        current_user: The current user from get_current_user dependency
        
    Returns:
        The current user if they are an admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def agent_required(current_user=Depends(get_current_user)):
    """
    Dependency to require agent role.
    
    Args:
        current_user: The current user from get_current_user dependency
        
    Returns:
        The current user if they are an agent or admin
        
    Raises:
        HTTPException: If user is not an agent or admin
    """
    if current_user.role not in [Role.AGENT.value, Role.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def customer_required(current_user=Depends(get_current_user)):
    """
    Dependency to require customer role.
    
    Args:
        current_user: The current user from get_current_user dependency
        
    Returns:
        The current user if they are a customer
        
    Raises:
        HTTPException: If user is not a customer
    """
    if current_user.role != Role.CUSTOMER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_active_superuser(
    current_user=Depends(get_current_user)
) -> "User":
    """
    Dependency to get current active superuser.
    
    Args:
        current_user: The current user from get_current_user dependency
        
    Returns:
        The current user if they are an active superuser
        
    Raises:
        HTTPException: If user is not a superuser or is inactive
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

__all__ = [
    'admin_required',
    'agent_required',
    'customer_required',
    'get_current_active_superuser',
    'require_role'
] 