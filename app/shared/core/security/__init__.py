from .jwt import jwt_service, get_current_user, get_current_customer
from .encryption import encryption_service
from enum import Enum

__all__ = [
    'jwt_service',
    'get_current_user',
    'get_current_customer',
    'encryption_service'
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