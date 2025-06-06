from enum import Enum
from typing import Optional, Union

from app.shared.core.security.auth import (
    authenticate_user,
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    get_current_customer,
    get_current_active_customer,
    get_current_tenant,
    Role
)

from app.shared.core.security.tokens import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    verify_jwt_token,
    generate_verification_token,
    generate_password_reset_token
)

from app.shared.core.security.security import (
    encrypt_value,
    decrypt_value,
    hash_code,
    verify_mfa_code
)

from app.shared.core.security.password_utils import (
    get_password_hash,
    verify_password
)

from app.shared.core.security.dependencies import (
    require_role,
    require_permission,
    get_user_permissions,
    admin_required,
    manager_required,
    agent_required,
    viewer_required
)

from app.shared.core.security.permissions import (
    PermissionService,
    require_admin,
    require_manager,
    require_agent,
    require_user_management,
    require_property_management,
    require_customer_management,
    require_system_management,
)

class UserRole(str, Enum):
    """
    User role enumeration.
    """
    ADMIN = "admin"
    AGENT = "agent"
    CUSTOMER = "customer"
    USER = "user"

__all__ = [
    # Auth functions
    'authenticate_user',
    'get_current_user',
    'get_current_active_user',
    'get_current_superuser',
    'get_current_customer',
    'get_current_active_customer',
    'get_current_tenant',
    'Role',
    
    # Token functions
    'create_access_token',
    'create_refresh_token',
    'decode_access_token',
    'decode_refresh_token',
    'verify_jwt_token',
    'generate_verification_token',
    'generate_password_reset_token',
    
    # Security functions
    'encrypt_value',
    'decrypt_value',
    'hash_code',
    'verify_mfa_code',
    'get_password_hash',
    'verify_password',
    'PermissionService',
    'require_admin',
    'require_manager',
    'require_agent',
    'require_user_management',
    'require_property_management',
    'require_customer_management',
    'require_system_management',
    'UserRole',
] 