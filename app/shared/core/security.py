from datetime import datetime, timedelta
from typing import Any, Optional, Union, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.shared.core.config import settings
from enum import Enum
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, ValidationError
from app.shared.models.user import User
from app.shared.models.customer import Customer
from app.shared.db.session import get_db
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    VIEWER = "viewer"

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
def manager_required():
    return require_role([UserRole.ADMIN, UserRole.MANAGER])

def agent_required():
    return require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT])

def viewer_required():
    return require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT, UserRole.VIEWER]) 