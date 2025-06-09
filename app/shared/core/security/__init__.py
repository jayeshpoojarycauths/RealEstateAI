"""
Security module initialization.
"""

from enum import Enum
from typing import Optional, Union

# Import roles first to avoid circular imports
from app.shared.core.security.role_types import Role

# Import auth functions
from app.shared.core.security.auth import (
    get_current_user,
    get_current_active_user,
    get_password_hash,
    verify_password
)

# Import customer functions from deps
from app.shared.core.infrastructure.deps import (
    get_current_customer,
    get_current_active_customer
)

# Import token functions
from app.shared.core.security.tokens import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    verify_jwt_token,
    generate_verification_token,
    generate_password_reset_token
)

# Import security utilities
from app.shared.core.security.security import (
    encrypt_value,
    decrypt_value,
    hash_code,
    verify_mfa_code
)

# Import dependencies
from app.shared.core.security.dependencies import (
    admin_required,
    agent_required,
    customer_required,
    get_current_active_superuser,
    require_role
)

# Import permissions
from app.shared.core.security.permissions import (
    Permission,
    PermissionService,
    permission_service,
    require_admin,
    require_agent,
    require_customer,
    require_user_management,
    require_property_management,
    require_customer_management,
    require_system_management,
    check_permission,
    has_permission,
    get_user_permissions
)

# Import RBAC
from app.shared.core.security.rbac import (
    RBACService,
    rbac_service
)

# Re-export everything needed by other modules
__all__ = [
    # Auth
    'create_access_token',
    'get_current_user',
    'get_current_active_user',
    'get_password_hash',
    'verify_password',
    
    # Dependencies
    'admin_required',
    'agent_required',
    'customer_required',
    'require_role',
    
    # Roles
    'Role',
    
    # RBAC
    'Permission',
    'RBACService',
    'require_admin',
    'require_agent',
    'rbac_service',
    
    # Auth functions
    "get_current_customer",
    "get_current_active_customer"
    
    # Token functions
    "create_refresh_token",
    "decode_access_token",
    "decode_refresh_token",
    "verify_jwt_token",
    "generate_verification_token",
    "generate_password_reset_token",
    
    # Security utilities
    "encrypt_value",
    "decrypt_value",
    "hash_code",
    "verify_mfa_code",
    
    # Permissions
    "PermissionService",
    "permission_service",
    "require_customer",
    "require_user_management",
    "require_property_management",
    "require_customer_management",
    "require_system_management",
    "check_permission",
    "has_permission",
    "get_user_permissions"
] 