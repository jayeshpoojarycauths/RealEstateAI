from datetime import datetime, timedelta
from typing import Any, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.shared.core.config import settings
from app.shared.core.security.auth import get_current_user
from app.shared.db.session import get_db
from app.shared.models.customer import Customer
from app.shared.models.user import User
from sqlalchemy.orm import Session
from fastapi import Depends
from app.shared.models.user import User
from app.shared.db.session import get_db
from fastapi import HTTPException
from datetime import datetime
from typing import Any
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import Depends
from app.shared.models.user import User
from app.shared.db.session import get_db
from fastapi import HTTPException
from datetime import datetime
from typing import Any
from datetime import timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: list[str] = []

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional expiration time delta
        
    Returns:
        str: JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional expiration time delta
        
    Returns:
        str: JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def generate_verification_token(
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate an email verification token.
    
    Args:
        email: User's email address
        expires_delta: Optional expiration time delta
        
    Returns:
        str: JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)  # 24 hours by default
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "email_verification"
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def generate_password_reset_token(
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a password reset token.
    
    Args:
        email: User's email address
        expires_delta: Optional expiration time delta
        
    Returns:
        str: JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour by default
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "password_reset"
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.JWTError:
        return None

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_customer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Customer:
    """Get current customer from user."""
    customer = db.query(Customer).filter(Customer.id == current_user.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer

# Alias for backward compatibility
get_current_tenant = get_current_customer 