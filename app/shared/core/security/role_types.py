"""
Role type definitions.
"""

from enum import Enum

class Role(str, Enum):
    """User role definitions."""
    ADMIN = "admin"
    AGENT = "agent"
    CUSTOMER = "customer"
    GUEST = "guest"

__all__ = ["Role"] 