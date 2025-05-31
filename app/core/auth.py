from typing import Optional, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import User, Customer
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.db.session import get_db
from app.schemas.user import TokenPayload
from pydantic import ValidationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise AuthenticationError("Could not validate credentials")

    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise AuthenticationError("User not found")
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise AuthorizationError("Inactive user")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise AuthorizationError("Not enough permissions")
    return current_user

async def get_current_customer(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Customer:
    """Get current customer from user."""
    customer = db.query(Customer).filter(Customer.id == current_user.customer_id).first()
    if not customer:
        raise AuthenticationError("Customer not found")
    return customer

async def get_current_active_customer(
    current_customer: Customer = Depends(get_current_customer)
) -> Customer:
    """Get current active customer."""
    if not current_customer.is_active:
        raise AuthorizationError("Inactive customer")
    return current_customer

def get_current_tenant(
    current_customer: Customer = Depends(get_current_customer)
) -> str:
    """Get current tenant identifier."""
    return current_customer.tenant_id 