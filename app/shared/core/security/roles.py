from enum import Enum

class Role(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    CUSTOMER = "customer" 