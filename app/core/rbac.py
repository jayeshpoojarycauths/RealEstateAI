from enum import Enum
from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user
from app.core.exceptions import AuthorizationException
from app.core.messages import MessageCode, Messages

class Role(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    CUSTOMER = "customer"

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
ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    Role.ADMIN: [
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
    ],
    Role.MANAGER: [
        Permission.READ_USER,
        Permission.CREATE_PROPERTY,
        Permission.READ_PROPERTY,
        Permission.UPDATE_PROPERTY,
        Permission.DELETE_PROPERTY,
        Permission.CREATE_CUSTOMER,
        Permission.READ_CUSTOMER,
        Permission.UPDATE_CUSTOMER,
    ],
    Role.AGENT: [
        Permission.READ_PROPERTY,
        Permission.CREATE_CUSTOMER,
        Permission.READ_CUSTOMER,
        Permission.UPDATE_CUSTOMER,
    ],
    Role.CUSTOMER: [
        Permission.READ_PROPERTY,
        Permission.READ_CUSTOMER,
    ],
}

class PermissionService:
    """Service for managing permissions and role-based access control."""
    
    @staticmethod
    def get_role_permissions(role: Role) -> List[Permission]:
        """Get permissions for a given role."""
        return ROLE_PERMISSIONS.get(role, [])
    
    @staticmethod
    def has_permission(role: Role, permission: Permission) -> bool:
        """Check if a role has a specific permission."""
        return permission in ROLE_PERMISSIONS.get(role, [])
    
    @staticmethod
    def require_permission(permission: Permission):
        """Dependency for requiring a specific permission."""
        def dependency(current_user: Any = Depends(get_current_user)):
            if not PermissionService.has_permission(current_user.role, permission):
                raise AuthorizationException(
                    message_code=MessageCode.AUTH_INSUFFICIENT_PERMISSIONS,
                    details=f"Required permission: {permission}",
                    required_permission=permission
                )
            return current_user
        return dependency
    
    @staticmethod
    def require_roles(*roles: Role):
        """Dependency for requiring specific roles."""
        def dependency(current_user: Any = Depends(get_current_user)):
            if current_user.role not in roles:
                raise AuthorizationException(
                    message_code=MessageCode.AUTH_INSUFFICIENT_PERMISSIONS,
                    details=f"Required roles: {', '.join(role.value for role in roles)}",
                    required_roles=[role.value for role in roles]
                )
            return current_user
        return dependency

# Create permission service instance
permission_service = PermissionService()

# Export commonly used dependencies
require_admin = permission_service.require_roles(Role.ADMIN)
require_manager = permission_service.require_roles(Role.ADMIN, Role.MANAGER)
require_agent = permission_service.require_roles(Role.ADMIN, Role.MANAGER, Role.AGENT) 