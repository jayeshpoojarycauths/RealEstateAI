from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import User, Customer
from app.schemas.auth import User as UserSchema, UserCreate, UserUpdate
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
async def get_users(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve users for the current customer.
    """
    users = db.query(User).filter(
        User.customer_id == current_customer.id
    ).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserSchema)
async def create_user(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    user_in: UserCreate
) -> Any:
    """
    Create new user for the current customer.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists"
        )
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        customer_id=current_customer.id,
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    user_id: str,
    user_in: UserUpdate
) -> Any:
    """
    Update a user.
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.customer_id == current_customer.id
    ).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", response_model=UserSchema)
async def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    user_id: str
) -> Any:
    """
    Delete a user.
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.customer_id == current_customer.id
    ).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    return user 