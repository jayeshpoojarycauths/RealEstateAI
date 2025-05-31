from datetime import datetime, timedelta
from typing import Optional, Dict, List
from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.shared.core.config import settings
from app.models.models import User, Customer
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTService:
    def __init__(self):
        self._key_history: List[Dict[str, str]] = []
        self._current_key = settings.SECRET_KEY
        self._last_rotation = datetime.utcnow()

    def _rotate_key_if_needed(self):
        """Rotate JWT signing key if needed"""
        now = datetime.utcnow()
        if (now - self._last_rotation).days >= settings.JWT_KEY_ROTATION_DAYS:
            # Generate new key
            new_key = secrets.token_urlsafe(32)
            
            # Add current key to history
            self._key_history.append({
                "key": self._current_key,
                "created_at": self._last_rotation.isoformat()
            })
            
            # Keep only recent keys
            if len(self._key_history) > settings.JWT_KEY_HISTORY_SIZE:
                self._key_history.pop(0)
            
            # Update current key
            self._current_key = new_key
            self._last_rotation = now

    def create_access_token(self, user: User, customer: Customer) -> str:
        """Create a new access token"""
        self._rotate_key_if_needed()
        
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": str(user.id),
            "customer_id": str(customer.id),
            "exp": expire,
            "type": "access"
        }
        
        return jwt.encode(to_encode, self._current_key, algorithm=settings.ALGORITHM)

    def create_refresh_token(self, user: User, customer: Customer) -> str:
        """Create a new refresh token"""
        self._rotate_key_if_needed()
        
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": str(user.id),
            "customer_id": str(customer.id),
            "exp": expire,
            "type": "refresh"
        }
        
        return jwt.encode(to_encode, self._current_key, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str) -> Dict:
        """Verify a JWT token"""
        try:
            # Try current key
            try:
                return jwt.decode(token, self._current_key, algorithms=[settings.ALGORITHM])
            except jwt.InvalidTokenError:
                # Try historical keys
                for key_data in self._key_history:
                    try:
                        return jwt.decode(token, key_data["key"], algorithms=[settings.ALGORITHM])
                    except jwt.InvalidTokenError:
                        continue
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

def get_current_user(token: str) -> Optional[User]:
    """Get the current user from a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return User.query.get(user_id)
    except JWTError:
        return None

def get_current_customer(token: str) -> Optional[Customer]:
    """Get the current customer from a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        customer_id: str = payload.get("customer_id")
        if customer_id is None:
            return None
        return Customer.query.get(customer_id)
    except JWTError:
        return None

jwt_service = JWTService() 