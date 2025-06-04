from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from app.shared.core.config import settings
from app.shared.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    UserRole
)
from app.shared.core.exceptions import (
    AuthenticationException,
    ValidationException,
    ServiceUnavailableException
)
from app.shared.core.email import (
    send_verification_email,
    send_password_reset_email,
    send_mfa_code_email
)
from app.shared.api.deps import get_current_active_user
from app.shared.models.user import User
from app.shared.schemas.auth import (
    Token,
    TokenPayload,
    UserCreate,
    UserLogin,
    PasswordReset,
    PasswordResetConfirm,
    MFAVerify
)
from app.shared.schemas.user import UserResponse
from app.shared.db.session import get_db
from app.auth.services.auth import AuthService

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    try:
        user = await AuthService(db).authenticate(
            email=form_data.username,
            password=form_data.password
        )
        if not user:
            raise AuthenticationException("Incorrect email or password")
        if not user.is_active:
            raise AuthenticationException("Inactive user")
        
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise AuthenticationException(str(e))

@router.post("/register", response_model=UserResponse)
async def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """
    Register new user.
    """
    try:
        user = await AuthService(db).register(user_in)
        return user
    except Exception as e:
        raise ValidationException(str(e))

@router.post("/password-reset", response_model=Dict[str, str])
async def password_reset(
    *,
    db: Session = Depends(get_db),
    reset_in: PasswordReset
) -> Any:
    """
    Request password reset.
    """
    try:
        await AuthService(db).request_password_reset(reset_in.email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise ServiceUnavailableException(
            detail=f"Error sending password reset email: {str(e)}"
        )

@router.post("/password-reset/confirm", response_model=Dict[str, str])
async def password_reset_confirm(
    *,
    db: Session = Depends(get_db),
    reset_in: PasswordResetConfirm
) -> Any:
    """
    Confirm password reset.
    """
    try:
        await AuthService(db).confirm_password_reset(
            token=reset_in.token,
            new_password=reset_in.new_password
        )
        return {"message": "Password reset successful"}
    except Exception as e:
        raise ValidationException(str(e))

@router.post("/mfa/verify", response_model=Dict[str, str])
async def verify_mfa(
    *,
    db: Session = Depends(get_db),
    mfa_in: MFAVerify
) -> Any:
    """
    Verify MFA code.
    """
    try:
        await AuthService(db).verify_mfa(
            user_id=mfa_in.user_id,
            code=mfa_in.code
        )
        return {"message": "MFA verification successful"}
    except Exception as e:
        raise ValidationException(str(e))

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user.
    """
    return current_user 