from app.shared.core.security.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user
)
from app.shared.core.security.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from app.shared.core.security.roles import Role, UserRole
from app.shared.core.security.permissions import Permission, check_permission

__all__ = [
    'authenticate_user',
    'create_access_token',
    'get_current_user',
    'get_current_active_user',
    'verify_password',
    'get_password_hash',
    'decode_access_token',
    'Role',
    'UserRole',
    'Permission',
    'check_permission'
]

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    VIEWER = "viewer"
    CUSTOMER = "customer"

    @classmethod
    def get_all_roles(cls) -> list[str]:
        return [role.value for role in cls]

    @classmethod
    def is_valid_role(cls, role: str) -> bool:
        return role in cls.get_all_roles() 