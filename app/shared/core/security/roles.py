from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from functools import wraps
from fastapi import HTTPException, Depends

if TYPE_CHECKING:
    from app.shared.models.user import User
    from app.shared.core.security.auth import get_current_user

class Role(str, Enum):
    """
    User role enumeration.
    """
    PLATFORM_ADMIN = "platform_admin"
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    ANALYST = "analyst"
    AUDITOR = "auditor"
    VIEWER = "viewer"
    CUSTOMER = "customer"
    USER = "user"

class Permission(str, Enum):
    """
    Permission enumeration.
    """
    MANAGE_USERS = "manage_users"
    MANAGE_LEADS = "manage_leads"
    MANAGE_PROJECTS = "manage_projects"
    VIEW_REPORTS = "view_reports"
    MANAGE_SETTINGS = "manage_settings"
    MANAGE_AGENTS = "manage_agents"
    MANAGE_CUSTOMERS = "manage_customers"

def require_role(roles: List[Role]):
    """
    Decorator to require specific roles for access.
    
    Args:
        roles: List of roles that are allowed to access the endpoint
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: "User" = Depends(get_current_user), **kwargs):
            if current_user.role not in roles:
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_permission(permissions: List[Permission]):
    """
    Decorator to require specific permissions for access.
    
    Args:
        permissions: List of permissions that are allowed to access the endpoint
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: "User" = Depends(get_current_user), **kwargs):
            user_permissions = get_user_permissions(current_user.role)
            if not any(perm in user_permissions for perm in permissions):
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def get_user_permissions(role: Role) -> List[Permission]:
    """
    Get permissions for a given role.
    
    Args:
        role: The user's role
        
    Returns:
        List of permissions for the role
    """
    role_permissions = {
        Role.PLATFORM_ADMIN: [
            Permission.MANAGE_USERS,
            Permission.MANAGE_LEADS,
            Permission.MANAGE_PROJECTS,
            Permission.VIEW_REPORTS,
            Permission.MANAGE_SETTINGS,
            Permission.MANAGE_AGENTS,
            Permission.MANAGE_CUSTOMERS
        ],
        Role.SUPERADMIN: [
            Permission.MANAGE_USERS,
            Permission.MANAGE_LEADS,
            Permission.MANAGE_PROJECTS,
            Permission.VIEW_REPORTS,
            Permission.MANAGE_SETTINGS,
            Permission.MANAGE_AGENTS,
            Permission.MANAGE_CUSTOMERS
        ],
        Role.ADMIN: [
            Permission.MANAGE_USERS,
            Permission.MANAGE_LEADS,
            Permission.MANAGE_PROJECTS,
            Permission.VIEW_REPORTS,
            Permission.MANAGE_SETTINGS,
            Permission.MANAGE_AGENTS,
            Permission.MANAGE_CUSTOMERS
        ],
        Role.MANAGER: [
            Permission.MANAGE_LEADS,
            Permission.MANAGE_PROJECTS,
            Permission.VIEW_REPORTS,
            Permission.MANAGE_AGENTS,
            Permission.MANAGE_CUSTOMERS
        ],
        Role.AGENT: [
            Permission.MANAGE_LEADS,
            Permission.MANAGE_PROJECTS,
            Permission.VIEW_REPORTS
        ],
        Role.ANALYST: [
            Permission.VIEW_REPORTS,
            Permission.MANAGE_PROJECTS
        ],
        Role.AUDITOR: [
            Permission.VIEW_REPORTS
        ],
        Role.VIEWER: [
            Permission.VIEW_REPORTS
        ],
        Role.CUSTOMER: [
            Permission.VIEW_REPORTS
        ],
        Role.USER: []
    }
    return role_permissions.get(role, [])

__all__ = [
    "Role",
    "Permission",
    "require_role",
    "require_permission",
    "get_user_permissions"
] 