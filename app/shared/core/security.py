from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.shared.core.config import settings
from fastapi import Depends
from app.shared.models.user import User
from fastapi import HTTPException
from datetime import datetime
from datetime import timedelta
from fastapi import Depends
from app.shared.models.user import User
from fastapi import HTTPException
from datetime import datetime
from datetime import timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"
    CUSTOMER = "customer"
    GUEST = "guest"

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: List[UserRole] = []

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
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

def require_role(required_roles: List[UserRole]):
    def decorator(token_data: TokenData = Depends(verify_token)):
        if not any(role in token_data.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return token_data
    return decorator

# Role-based access control decorators
def admin_required():
    return require_role([UserRole.ADMIN])

def agent_required():
    return require_role([UserRole.ADMIN, UserRole.AGENT])

def customer_required():
    return require_role([UserRole.ADMIN, UserRole.AGENT, UserRole.CUSTOMER])

def guest_required():
    return require_role([UserRole.ADMIN, UserRole.AGENT, UserRole.CUSTOMER, UserRole.GUEST]) 