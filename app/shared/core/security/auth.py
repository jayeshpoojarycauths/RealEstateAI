from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.shared.core.config import settings
from app.shared.models.user import User
from app.shared.core.exceptions import AuthenticationException, AuthorizationException
from app.shared.db.session import get_db
from app.shared.schemas.token import TokenPayload
from app.shared.core.auth import (
    get_current_user,
    get_current_active_user,
    get_current_superuser
)
from app.shared.core.security.roles import Role
from app.shared.models.customer import Customer

async def get_current_customer(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Customer:
    """Get current customer from user."""
    customer = db.query(Customer).filter(Customer.id == current_user.customer_id).first()
    if not customer:
        raise AuthenticationException("Customer not found")
    return customer

async def get_current_active_customer(
    current_customer: Customer = Depends(get_current_customer)
) -> Customer:
    """Get current active customer."""
    if not current_customer.is_active:
        raise AuthorizationException("Inactive customer")
    return current_customer

def get_current_tenant(
    current_customer: Customer = Depends(get_current_customer)
) -> str:
    """Get current tenant identifier."""
    return current_customer.tenant_id

# Re-export commonly used dependencies
__all__ = [
    'get_current_user',
    'get_current_active_user',
    'get_current_superuser',
    'Role',
    'TokenPayload'
] 