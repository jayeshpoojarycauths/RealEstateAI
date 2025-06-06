from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.shared.models.user import User

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

__all__ = [
    "Role"
] 