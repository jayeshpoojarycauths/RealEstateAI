from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from app.shared.db.session import get_db
from app.shared.core.security import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    get_current_customer,
    get_current_active_customer,
    get_current_tenant
)

# Re-export auth dependencies
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "get_current_customer",
    "get_current_active_customer",
    "get_current_tenant"
] 