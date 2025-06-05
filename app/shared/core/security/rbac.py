"""
Role-Based Access Control (RBAC) Module

This module implements a role-based access control system for the Real Estate AI platform.
It defines permissions, roles, and provides utilities for permission checking and role-based access control.

Key Components:
- Permission: Enum defining all system permissions
- ROLE_PERMISSIONS: Mapping of roles to their allowed permissions
- PermissionService: Service class for managing permissions and RBAC

Usage:
    from app.shared.core.security.rbac import require_admin, require_manager, require_agent

    @router.get("/admin-only")
    @require_admin
    async def admin_only_endpoint():
        return {"message": "Admin access granted"}
"""

from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from app.shared.core.infrastructure.deps import get_current_user
from app.shared.core.security.roles import Role
from app.shared.core.exceptions import PermissionDenied
from app.shared.core.communication.messages import Messages
from enum import Enum
from sqlalchemy.orm import Session
from app.shared.models.user import User
from app.shared.db.session import get_db
from app.shared.core.security.permissions import Permission

class Permission(str, Enum):
    """
    System permissions enum.
    
    This enum defines all possible permissions in the system, organized by category:
    - User Management: Permissions for managing users
    - Property Management: Permissions for managing properties
    - Customer Management: Permissions for managing customers
    - System Management: Permissions for system-level operations
    """
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

"""
Mapping of roles to their allowed permissions.

This dictionary defines which permissions are granted to each role in the system.
The permissions are organized in a hierarchical structure where:
- ADMIN has all permissions
- MANAGER has a subset of permissions
- AGENT has basic operational permissions
- CUSTOMER has minimal read-only permissions
"""

class RBACService:
    """Service for role-based access control."""
    
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
        def dependency(current_user: User):
            if not RBACService.has_permission(current_user.role, permission):
                raise PermissionDenied(
                    detail=f"Required permission: {permission}"
                )
            return current_user
        return dependency
    
    @staticmethod
    def require_roles(*roles: Role):
        """Dependency for requiring specific roles."""
        def dependency(current_user: User):
            if current_user.role not in roles:
                raise PermissionDenied(
                    detail=f"Required roles: {', '.join(role.value for role in roles)}"
                )
            return current_user
        return dependency

# Create RBAC service instance
rbac_service = RBACService()

# Export commonly used dependencies
require_admin = rbac_service.require_roles(Role.ADMIN)
require_manager = rbac_service.require_roles(Role.ADMIN, Role.MANAGER)
require_agent = rbac_service.require_roles(Role.ADMIN, Role.MANAGER, Role.AGENT)

__all__ = [
    'RBACService',
    'rbac_service',
    'require_admin',
    'require_manager',
    'require_agent',
] 