
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.shared.core.security.auth import get_current_user
from app.shared.core.security.jwt import verify_token
from app.shared.db.session import get_db
from app.shared.models.customer import Customer
from app.shared.models.user import User
from sqlalchemy.orm import Session
from fastapi import Depends
from app.shared.models.user import User
from app.shared.db.session import get_db
from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from app.shared.models.user import User
from app.shared.db.session import get_db
from fastapi import HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_customer(
    current_user: User = Depends(get_current_active_user),
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

async def get_current_active_customer(
    current_customer: Customer = Depends(get_current_customer)
) -> Customer:
    """Get current active customer."""
    if not current_customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive customer"
        )
    return current_customer 