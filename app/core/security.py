from datetime import datetime, timedelta
from typing import Any, Union, List, Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from functools import wraps
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from app.models.models import User, Customer
from app.core.password_utils import verify_password, get_password_hash
from app.core.constants import ALGORITHM
from app.api import deps
from sqlalchemy.orm import Session
import uuid

# Security constants
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    jti: Optional[str] = None
) -> str:
    """Create a JWT access token with JTI claim."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # Generate JTI if not provided
    if not jti:
        jti = str(uuid.uuid4())
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "jti": jti,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

class UserRole:
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    VIEWER = "viewer"

def get_current_customer(
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
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

def require_role(roles: List[str]):
    """Decorator to require specific role(s) for an endpoint."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            if current_user.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def admin_required():
    """Decorator to require admin role."""
    return require_role([UserRole.ADMIN])

def manager_required():
    """Decorator to require manager role."""
    return require_role([UserRole.ADMIN, UserRole.MANAGER])

def agent_required():
    """Decorator to require agent role."""
    return require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT])

def viewer_required():
    """Decorator to require viewer role."""
    return require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT, UserRole.VIEWER]) 