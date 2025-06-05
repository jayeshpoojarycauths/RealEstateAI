from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.shared.core.config import settings
from app.shared.models.user import User
from app.shared.core.exceptions import AuthenticationException, AuthorizationException
from app.shared.db.session import get_db
from app.shared.schemas.token import TokenPayload
from app.shared.core.security.security import verify_password
from app.shared.core.security.roles import Role
from app.shared.models.customer import Customer

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise AuthenticationException("Could not validate credentials")
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise AuthenticationException("User not found")
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise AuthorizationException("Inactive user")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise AuthorizationException("Not enough permissions")
    return current_user

def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> Optional[User]:
    """
    Authenticate a user with email and password.
    
    Args:
        db: Database session
        email: User's email
        password: User's password
        
    Returns:
        User object if authentication successful, None otherwise
        
    Raises:
        AuthenticationException: If user not found or password invalid
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise AuthenticationException("User not found")
    if not verify_password(password, user.hashed_password):
        raise AuthenticationException("Invalid password")
    return user

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
    'authenticate_user',
    'get_current_user',
    'get_current_active_user',
    'get_current_superuser',
    'get_current_customer',
    'get_current_active_customer',
    'get_current_tenant',
    'Role',
    'TokenPayload'
] 