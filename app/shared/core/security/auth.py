from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.shared.core.config import settings
from app.shared.core.security.security import verify_password, create_access_token, create_refresh_token, decode_access_token, decode_refresh_token
from app.shared.models.user import User
from app.shared.db.session import get_db
from app.shared.core.exceptions import AuthenticationException
from app.shared.core.security.roles import Role
from app.shared.models.customer import Customer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def create_access_token(subject: Union[str, int], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Optional expiration time delta
        
    Returns:
        str: The encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, int]) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: The subject of the token (usually user ID)
        
    Returns:
        str: The encoded JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_jwt_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current authenticated user.
    
    Args:
        token: The JWT token from the request
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If user is not found or inactive
    """
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User: The active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_superuser(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get the current superuser.
    
    Args:
        current_user: The current active user
        
    Returns:
        User: The superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
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
        raise AuthenticationException("Inactive customer")
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
    'TokenPayload',
    'create_access_token',
    'create_refresh_token',
    'decode_access_token',
    'decode_refresh_token'
] 