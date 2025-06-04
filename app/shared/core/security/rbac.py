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
from app.shared.core.security.roles import UserRole
from app.shared.core.exceptions import PermissionDenied
from app.shared.core.communication.messages import Messages
from enum import Enum

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
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.ADMIN: [
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
    UserRole.MANAGER: [
        Permission.READ_USER,
        Permission.CREATE_PROPERTY,
        Permission.READ_PROPERTY,
        Permission.UPDATE_PROPERTY,
        Permission.DELETE_PROPERTY,
        Permission.CREATE_CUSTOMER,
        Permission.READ_CUSTOMER,
        Permission.UPDATE_CUSTOMER,
    ],
    UserRole.AGENT: [
        Permission.READ_PROPERTY,
        Permission.CREATE_CUSTOMER,
        Permission.READ_CUSTOMER,
        Permission.UPDATE_CUSTOMER,
    ],
    UserRole.CUSTOMER: [
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

class PermissionService:
    """
    Service for managing permissions and role-based access control.
    
    This service provides methods for:
    - Checking if a role has specific permissions
    - Getting all permissions for a role
    - Creating FastAPI dependencies for permission-based access control
    - Creating FastAPI dependencies for role-based access control
    """
    
    @staticmethod
    def get_role_permissions(role: UserRole) -> List[Permission]:
        """
        Get all permissions for a given role.
        
        Args:
            role: The role to get permissions for
            
        Returns:
            List of permissions granted to the role
        """
        return ROLE_PERMISSIONS.get(role, [])
    
    @staticmethod
    def has_permission(role: UserRole, permission: Permission) -> bool:
        """
        Check if a role has a specific permission.
        
        Args:
            role: The role to check
            permission: The permission to check for
            
        Returns:
            True if the role has the permission, False otherwise
        """
        return permission in ROLE_PERMISSIONS.get(role, [])
    
    @staticmethod
    def require_permission(permission: Permission):
        """
        Create a FastAPI dependency that requires a specific permission.
        
        Args:
            permission: The permission required to access the endpoint
            
        Returns:
            FastAPI dependency that checks for the required permission
        """
        def dependency(current_user: Any = Depends(get_current_user)):
            if not PermissionService.has_permission(current_user.role, permission):
                raise PermissionDenied(
                    message_code=MessageCode.AUTH_INSUFFICIENT_PERMISSIONS,
                    details=f"Required permission: {permission}",
                    required_permission=permission
                )
            return current_user
        return dependency
    
    @staticmethod
    def require_roles(*roles: UserRole):
        """
        Create a FastAPI dependency that requires specific roles.
        
        Args:
            *roles: The roles allowed to access the endpoint
            
        Returns:
            FastAPI dependency that checks for the required roles
        """
        def dependency(current_user: Any = Depends(get_current_user)):
            if current_user.role not in roles:
                raise PermissionDenied(
                    message_code=MessageCode.AUTH_INSUFFICIENT_PERMISSIONS,
                    details=f"Required roles: {', '.join(role.value for role in roles)}",
                    required_roles=[role.value for role in roles]
                )
            return current_user
        return dependency

# Create permission service instance
permission_service = PermissionService()

# Export commonly used dependencies
require_admin = permission_service.require_roles(UserRole.ADMIN)
require_manager = permission_service.require_roles(UserRole.ADMIN, UserRole.MANAGER)
require_agent = permission_service.require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT) 