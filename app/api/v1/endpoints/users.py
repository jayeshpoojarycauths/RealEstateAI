from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.rbac import Role, Permission, require_admin, permission_service
from app.core.exceptions import ResourceNotFoundException, MessageCode
from app.core.logging import logger, audit_logger
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash
from app.core.messages import Messages

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user."""
    try:
        # Check if user already exists
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log the action
        audit_logger.info(
            f"User created: {new_user.email}",
            extra={
                "user_id": new_user.id,
                "created_by": current_user.id,
                "role": new_user.role
            }
        )
        
        return new_user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(permission_service.require_permission(Permission.READ_USER))
):
    """List all users."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(permission_service.require_permission(Permission.READ_USER))
):
    """Get a specific user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(
            message_code=MessageCode.USER_NOT_FOUND,
            resource_type="User",
            resource_id=user_id
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(permission_service.require_permission(Permission.UPDATE_USER))
):
    """Update a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(
            message_code=MessageCode.USER_NOT_FOUND,
            resource_type="User",
            resource_id=user_id
        )
    
    # Update user fields
    for field, value in user_data.dict(exclude_unset=True).items():
        if field == "password" and value:
            value = get_password_hash(value)
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Log the action
    audit_logger.info(
        f"User updated: {user.email}",
        extra={
            "user_id": user.id,
            "updated_by": current_user.id,
            "updated_fields": list(user_data.dict(exclude_unset=True).keys())
        }
    )
    
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(permission_service.require_permission(Permission.DELETE_USER))
):
    """Delete a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(
            message_code=MessageCode.USER_NOT_FOUND,
            resource_type="User",
            resource_id=user_id
        )
    
    # Log the action before deletion
    audit_logger.info(
        f"User deleted: {user.email}",
        extra={
            "user_id": user.id,
            "deleted_by": current_user.id,
            "role": user.role
        }
    )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"} 