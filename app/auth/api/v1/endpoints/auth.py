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

from app.shared.core import security
from app.shared.core.config import settings
from app.shared.db.session import get_db
from app.models.models import User, RefreshToken, LoginAttempt, MFASettings, PasswordReset
from app.auth.schemas.user import (
    Token, User as UserSchema, MFASettings as MFASettingsSchema,
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

# Rate limiting constants
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_WINDOW = 15  # minutes
LOCKOUT_DURATION = 30  # minutes

def check_rate_limit(db: Session, email: str, ip_address: str) -> None:
    """Check if user has exceeded login attempt limits"""
    recent_attempts = db.query(LoginAttempt).filter(
        and_(
            LoginAttempt.email == email,
            LoginAttempt.attempt_time >= datetime.utcnow() - timedelta(minutes=LOGIN_ATTEMPT_WINDOW)
        )
    ).count()

    if recent_attempts >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Please try again in {LOCKOUT_DURATION} minutes."
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
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Login for access token."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
async def verify_mfa(
    *,
    db: Session = Depends(get_db),
    mfa_data: MFAVerify
) -> Any:
    """Verify MFA code and get access token."""
    auth_service = AuthService(db)
    user = await auth_service.verify_mfa(mfa_data.code, mfa_data.method)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
def enable_mfa(
    mfa_data: MFAVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Enable MFA after verification"""
    mfa_settings = db.query(MFASettings).filter(MFASettings.user_id == current_user.id).first()
    if not mfa_settings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not set up"
        )

    # Verify TOTP code
    totp = pyotp.TOTP(mfa_settings.secret_key)
    if not totp.verify(mfa_data.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )

    # Enable MFA
    mfa_settings.is_enabled = True
    db.commit()

    return {"message": "MFA enabled successfully"}

@router.post("/request-password-reset")
def request_password_reset(
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
def reset_password(
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
    access_token = security.create_access_token(
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
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
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
            db_refresh_token.is_revoked = True
            db.commit()

    # Clear all auth cookies
    response.delete_cookie("access_token", httponly=True, secure=True, samesite="lax", path="/")
    response.delete_cookie("refresh_token", httponly=True, secure=True, samesite="lax", path="/")
    response.delete_cookie("csrf_token", secure=True, samesite="lax", path="/")

    return {"message": "Successfully logged out"} 