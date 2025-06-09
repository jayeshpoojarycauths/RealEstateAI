"""
Role-based access control definitions.
"""

from typing import TYPE_CHECKING

from app.shared.core.security.role_types import Role

if TYPE_CHECKING:
    from app.shared.models.user import User

__all__ = ["Role"] 