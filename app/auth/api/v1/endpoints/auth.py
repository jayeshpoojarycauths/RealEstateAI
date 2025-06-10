from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.services.auth import AuthService
from app.shared.api.deps import get_current_active_user
from app.shared.core.config import settings
from app.shared.core.exceptions import (AuthenticationException,
                                        ServiceUnavailableException,
                                        ValidationException)
from app.shared.core.security import (create_access_token)
from app.shared.db.session import get_db
from app.shared.models.user import User
from app.shared.schemas.auth import (MFAVerify, PasswordReset,
                                     PasswordResetConfirm, Token, UserCreate, UserLogin,
                                     ForgotPasswordRequest, ForgotUsernameRequest, PasswordResetRequest)
from app.shared.schemas.user import UserResponse
from fastapi import Request
from sqlalchemy.orm import Session
from fastapi import Depends
from app.shared.models.user import User
from app.shared.db.session import get_db
from datetime import datetime
from typing import Dict
from typing import Any
from datetime import timedelta
from fastapi import Request
from sqlalchemy.orm import Session
from fastapi import Depends
from app.shared.models.user import User
from app.shared.db.session import get_db
from datetime import datetime
from typing import Dict
from typing import Any
from datetime import timedelta

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login", response_model=Token)
async def login(
    *,
    db: Session = Depends(get_db),
    login_data: UserLogin
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_user(login_data)
        if not user:
            raise AuthenticationException("Incorrect username/email or password")
        if not user.is_active:
            raise AuthenticationException("Inactive user")
        
        access_token = await auth_service.create_access_token(user)
        
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
        auth_service = AuthService(db)
        user = await auth_service.create_user(user_in)
        return user
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

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

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        await auth_service.request_password_reset(request.email)
        return {"message": "If an account exists with this email, you will receive password reset instructions."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )

@router.post("/forgot-username")
async def forgot_username(request: ForgotUsernameRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        await auth_service.request_username_reminder(request.email)
        return {"message": "If an account exists with this email, you will receive your username."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )

@router.post("/reset-password")
async def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        await auth_service.reset_password(request.token, request.new_password)
        return {"message": "Password has been reset successfully"}
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting your password"
        ) 