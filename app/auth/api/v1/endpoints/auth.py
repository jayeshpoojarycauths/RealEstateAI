from datetime import timedelta, datetime
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import secrets
import json
import pyotp
import qrcode
import io
import base64
from sqlalchemy import and_, func
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.shared.core.exceptions import RateLimitError, AuthenticationError
from app.shared.core.config import settings
from app.shared.db.session import get_db
from app.models.models import User
from app.auth.models.auth import RefreshToken, LoginAttempt, MFASettings, PasswordReset
from app.auth.schemas.auth import (
    Token, MFASettings as MFASettingsSchema,
    PasswordResetRequest, PasswordReset as PasswordResetSchema,
    MFASetupResponse, MFAVerify, MFABackupCode
)
from app.core.password_utils import verify_password, get_password_hash
from app.shared.core.email import send_reset_password_email, send_mfa_code_email
from app.shared.core.sms import send_mfa_code_sms
from app.core.deps import get_current_active_user
from app.auth.services.auth import AuthService
from app.shared.core.security import create_access_token

router = APIRouter()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Rate limiting constants
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_WINDOW = 15  # minutes
LOCKOUT_DURATION = 30  # minutes
MFA_ATTEMPT_WINDOW = 5  # minutes
MAX_MFA_ATTEMPTS = 3

def check_rate_limit(db: Session, email: str, ip_address: str) -> None:
    """Check if user has exceeded login attempt limits"""
    recent_attempts = db.query(LoginAttempt).filter(
        and_(
            LoginAttempt.email == email,
            LoginAttempt.attempt_time >= datetime.utcnow() - timedelta(minutes=LOGIN_ATTEMPT_WINDOW)
        )
    ).count()

    if recent_attempts >= MAX_LOGIN_ATTEMPTS:
        raise RateLimitError(
            detail=f"Too many login attempts. Please try again in {LOCKOUT_DURATION} minutes."
        )

def check_mfa_rate_limit(db: Session, user_id: str) -> None:
    """Check if user has exceeded MFA verification attempts"""
    recent_attempts = db.query(LoginAttempt).filter(
        and_(
            LoginAttempt.user_id == user_id,
            LoginAttempt.attempt_time >= datetime.utcnow() - timedelta(minutes=MFA_ATTEMPT_WINDOW)
        )
    ).count()

    if recent_attempts >= MAX_MFA_ATTEMPTS:
        raise RateLimitError(
            detail=f"Too many MFA verification attempts. Please try again in {MFA_ATTEMPT_WINDOW} minutes."
        )

def record_login_attempt(
    db: Session,
    email: str,
    ip_address: str,
    user_agent: str,
    success: bool,
    user_id: str = None,
    failure_reason: str = None
) -> None:
    """Record a login attempt"""
    attempt = LoginAttempt(
        email=email,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        user_id=user_id,
        failure_reason=failure_reason
    )
    db.add(attempt)
    db.commit()

def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Login for access token."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(
        email=form_data.username,
        password=form_data.password,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )
    
    if not user:
        raise AuthenticationError(detail="Incorrect username or password")
    
    if user.mfa_enabled:
        return {
            "access_token": create_access_token(user.id),
            "token_type": "bearer",
            "requires_mfa": True
        }
    
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "requires_mfa": False
    }

@router.post("/verify-mfa", response_model=Token)
@limiter.limit("3/minute")
async def verify_mfa(
    request: Request,
    db: Session = Depends(get_db),
    mfa_data: MFAVerify
) -> Any:
    """Verify MFA code and get access token."""
    # Get user from token
    user = await get_current_active_user(request)
    
    auth_service = AuthService(db)
    if not await auth_service.verify_mfa(
        user=user,
        code=mfa_data.code,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    ):
        raise AuthenticationError(detail="Invalid MFA code")
    
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer"
    }

@router.post("/setup-mfa", response_model=MFASetupResponse)
async def setup_mfa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Setup MFA for the current user."""
    auth_service = AuthService(db)
    return await auth_service.setup_mfa(current_user)

@router.post("/generate-backup-codes", response_model=List[MFABackupCode])
async def generate_backup_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Generate new backup codes for the current user."""
    auth_service = AuthService(db)
    return await auth_service.generate_backup_codes(current_user)

@router.post("/enable-mfa")
async def enable_mfa(
    mfa_data: MFAVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Enable MFA after verification"""
    auth_service = AuthService(db)
    if not await auth_service.enable_mfa(current_user, mfa_data.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )

    return {"message": "MFA enabled successfully"}

@router.post("/request-password-reset")
@limiter.limit("3/hour")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Request a password reset"""
    user = db.query(User).filter(User.email == reset_request.email).first()
    if not user:
        # Don't reveal that the email doesn't exist
        return {"message": "If your email is registered, you will receive a password reset link"}

    # Generate reset token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    # Store reset token
    reset = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    db.add(reset)
    db.commit()

    # Send reset email
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    send_reset_password_email(user.email, reset_link)

    return {"message": "If your email is registered, you will receive a password reset link"}

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetSchema,
    db: Session = Depends(get_db)
) -> Any:
    """Reset password using token"""
    reset = db.query(PasswordReset).filter(
        and_(
            PasswordReset.token == reset_data.token,
            PasswordReset.expires_at > datetime.utcnow(),
            PasswordReset.is_used == False
        )
    ).first()

    if not reset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Update password
    user = db.query(User).filter(User.id == reset.user_id).first()
    user.password_hash = get_password_hash(reset_data.new_password)
    reset.is_used = True
    db.commit()

    return {"message": "Password reset successfully"}

@router.post("/refresh")
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    # Find refresh token in database
    db_refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.is_revoked == False
    ).first()

    if not db_refresh_token or not db_refresh_token.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Generate new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(db_refresh_token.user_id),
            "customer_id": str(db_refresh_token.customer_id)
        },
        expires_delta=access_token_expires
    )

    # Generate new CSRF token
    csrf_token = generate_csrf_token()

    # Set new cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "csrf_token": csrf_token
    }

@router.post("/logout")
async def logout(
    request: Request = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    response: Response = Depends()
) -> Any:
    """
    Logout user by clearing tokens and revoking refresh token
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        # Revoke refresh token
        db_refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        if db_refresh_token:
            auth_service = AuthService(db)
            await auth_service.invalidate_session(
                session_id=str(db_refresh_token.id),
                reason="user_logout"
            )

    # Clear all auth cookies
    response.delete_cookie("access_token", httponly=True, secure=True, samesite="lax", path="/")
    response.delete_cookie("refresh_token", httponly=True, secure=True, samesite="lax", path="/")
    response.delete_cookie("csrf_token", secure=True, samesite="lax", path="/")

    return {"message": "Successfully logged out"}

@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Change user's password."""
    auth_service = AuthService(db)
    success = await auth_service.change_password(
        user=current_user,
        current_password=current_password,
        new_password=new_password,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )
    
    if not success:
        raise AuthenticationError(detail="Invalid current password")
        
    return {"message": "Password changed successfully"} 