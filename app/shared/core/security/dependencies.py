from typing import List
from fastapi import HTTPException, Depends, status
from app.shared.core.security.roles import Role
from app.shared.core.security.auth import get_current_user

# If you have a Permission enum, import it as well
try:
    from app.shared.core.security.permissions import Permission
except ImportError:
    Permission = None

def require_role(roles: List[Role]):
    """
    Dependency to require specific roles for access.
    """
    def decorator(func):
        async def wrapper(*args, current_user = Depends(get_current_user), **kwargs):
            if current_user.role not in roles:
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_permission(permissions: List):
    """
    Dependency to require specific permissions for access.
    """
    def decorator(func):
        async def wrapper(*args, current_user = Depends(get_current_user), **kwargs):
            user_permissions = get_user_permissions(current_user.role)
            if not any(perm in user_permissions for perm in permissions):
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def get_user_permissions(role: Role) -> List:
    """
    Get permissions for a given role.
    """
    # This should be replaced with your actual permission logic
    if Permission is None:
        return []
    role_permissions = {
        Role.ADMIN: [Permission.MANAGE_USERS, Permission.MANAGE_LEADS],
        Role.MANAGER: [Permission.MANAGE_LEADS],
        # ... add other roles and permissions as needed ...
    }
    return role_permissions.get(role, [])

async def admin_required(current_user=Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def manager_required(current_user=Depends(get_current_user)):
    if current_user.role not in [Role.ADMIN, Role.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def agent_required(current_user=Depends(get_current_user)):
    if current_user.role not in [Role.ADMIN, Role.MANAGER, Role.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def viewer_required(current_user=Depends(get_current_user)):
    if current_user.role not in [Role.ADMIN, Role.MANAGER, Role.AGENT, Role.VIEWER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

__all__ = [
    "require_role",
    "require_permission",
    "get_user_permissions",
    "admin_required",
    "manager_required",
    "agent_required",
    "viewer_required"
] 