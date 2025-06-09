"""
Permission management module.
"""

from enum import Enum
from typing import Dict, Set, TYPE_CHECKING

from fastapi import HTTPException, status

from app.shared.core.exceptions import PermissionDenied
from app.shared.core.security.role_types import Role

if TYPE_CHECKING:
    from app.shared.models.user import User

class Permission(str, Enum):
    """System permissions."""
    # User Management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Property Management
    CREATE_PROPERTY = "create_property"
    READ_PROPERTY = "read_property"
    UPDATE_PROPERTY = "update_property"
    DELETE_PROPERTY = "delete_property"
    
    # Customer Management
    CREATE_CUSTOMER = "create_customer"
    READ_CUSTOMER = "read_customer"
    UPDATE_CUSTOMER = "update_customer"
    DELETE_CUSTOMER = "delete_customer"
    
    # System Management
    MANAGE_SYSTEM = "manage_system"
    VIEW_AUDIT_LOGS = "view_audit_logs"

# Role-Permission mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.CREATE_USER,
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.CREATE_PROPERTY,
        Permission.READ_PROPERTY,
        Permission.UPDATE_PROPERTY,
        Permission.DELETE_PROPERTY,
        Permission.CREATE_CUSTOMER,
        Permission.READ_CUSTOMER,
        Permission.UPDATE_CUSTOMER,
        Permission.DELETE_CUSTOMER,
        Permission.MANAGE_SYSTEM,
        Permission.VIEW_AUDIT_LOGS,
    },
    Role.AGENT: {
        Permission.READ_PROPERTY,
        Permission.CREATE_CUSTOMER,
        Permission.READ_CUSTOMER,
        Permission.UPDATE_CUSTOMER,
    },
    Role.CUSTOMER: {
        Permission.READ_PROPERTY,
        Permission.READ_CUSTOMER,
    },
    Role.GUEST: {
        Permission.READ_PROPERTY,
    },
}

def get_user_permissions(user: "User") -> Set[Permission]:
    """Get all permissions for a user."""
    return ROLE_PERMISSIONS.get(user.role, set())

def check_permission(
    required_permission: str,
    current_user: "User"
) -> bool:
    """Check if user has required permission."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    if current_user.is_superuser:
        return True
        
    user_permissions = get_user_permissions(current_user)
    return required_permission in user_permissions

def has_permission(
    required_permission: str,
    current_user: "User"
) -> bool:
    """Check if user has required permission without raising exception."""
    if not current_user.is_active:
        return False
        
    if current_user.is_superuser:
        return True
        
    user_permissions = get_user_permissions(current_user)
    return required_permission in user_permissions

class PermissionService:
    """Service for managing permissions and role-based access control."""
    
    @staticmethod
    def get_role_permissions(role: Role) -> Set[Permission]:
        """Get permissions for a given role."""
        return ROLE_PERMISSIONS.get(role, set())
    
    @staticmethod
    def has_permission(role: Role, permission: Permission) -> bool:
        """Check if a role has a specific permission."""
        return permission in ROLE_PERMISSIONS.get(role, set())
    
    @staticmethod
    def require_permission(permission: Permission):
        """Dependency for requiring a specific permission."""
        def dependency(current_user: "User"):
            if not PermissionService.has_permission(current_user.role, permission):
                raise PermissionDenied(
                    detail=f"Required permission: {permission}"
                )
            return current_user
        return dependency
    
    @staticmethod
    def require_roles(*roles: Role):
        """Dependency for requiring specific roles."""
        def dependency(current_user: "User"):
            if current_user.role not in roles:
                raise PermissionDenied(
                    detail=f"Required roles: {', '.join(role.value for role in roles)}"
                )
            return current_user
        return dependency

# Create permission service instance
permission_service = PermissionService()

# Export commonly used dependencies
require_admin = permission_service.require_roles(Role.ADMIN)
require_agent = permission_service.require_roles(Role.ADMIN, Role.AGENT)
require_customer = permission_service.require_roles(Role.ADMIN, Role.AGENT, Role.CUSTOMER)

# Export permission-based dependencies
require_user_management = permission_service.require_permission(Permission.CREATE_USER)
require_property_management = permission_service.require_permission(Permission.CREATE_PROPERTY)
require_customer_management = permission_service.require_permission(Permission.CREATE_CUSTOMER)
require_system_management = permission_service.require_permission(Permission.MANAGE_SYSTEM)

__all__ = [
    'Permission',
    'PermissionService',
    'permission_service',
    'require_admin',
    'require_agent',
    'require_customer',
    'require_user_management',
    'require_property_management',
    'require_customer_management',
    'require_system_management',
    'check_permission',
    'has_permission',
    'get_user_permissions',
    'init_dependencies'
] 