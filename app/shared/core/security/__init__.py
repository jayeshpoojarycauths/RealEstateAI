from enum import Enum
from typing import Optional, Union

from app.shared.core.security.auth import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    verify_jwt_token
)

from app.shared.core.security.security import (
    verify_mfa_code,
    encrypt_value,
    decrypt_value,
    hash_code
)

from app.shared.core.security.password_utils import (
    get_password_hash,
    verify_password
)

from app.shared.core.security.roles import (
    Role,
    Permission,
    require_role,
    require_permission,
    get_user_permissions
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
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "decode_refresh_token",
    "verify_jwt_token",
    "verify_mfa_code",
    "get_password_hash",
    "verify_password",
    "encrypt_value",
    "decrypt_value",
    "hash_code",
    "Role",
    "Permission",
    "PermissionService",
    "require_admin",
    "require_manager",
    "require_agent",
    "require_user_management",
    "require_property_management",
    "require_customer_management",
    "require_system_management",
    "UserRole",
    "require_role",
    "require_permission",
    "get_user_permissions"
] 