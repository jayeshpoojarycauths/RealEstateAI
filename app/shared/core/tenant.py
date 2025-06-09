from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.shared.db.session import get_db
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


async def get_customer_id(
    db: Session = Depends(get_db),
    current_user: User = Depends(lambda: None)  # This will be replaced with actual user dependency
) -> Optional[str]:
    """
    Get the customer ID for the current user.
    If no user is provided, returns None.
    """
    if not current_user:
        return None
    
    if not current_user.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any customer"
        )
    
    return str(current_user.customer_id) 