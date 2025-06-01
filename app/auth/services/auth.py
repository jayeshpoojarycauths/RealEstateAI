from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import User, Customer, MFASettings, UserSession
from app.auth.models.auth import LoginAttempt, PasswordReset
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings
from app.shared.core.exceptions import ValidationError, AuthenticationError
from app.shared.core.audit import AuditService
import pyotp
import secrets
import qrcode
import io
import base64
import re
import json
import uuid

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def validate_password_complexity(self, password: str) -> None:
        """Validate password complexity requirements."""
        if len(password) < 8:
            raise ValidationError(detail="Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', password):
            raise ValidationError(detail="Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValidationError(detail="Password must contain at least one lowercase letter")
        if not re.search(r'\d', password):
            raise ValidationError(detail="Password must contain at least one number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(detail="Password must contain at least one special character")

    async def authenticate_user(self, email: str, password: str, ip_address: str, user_agent: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            self.audit_service.log_login_failure(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                reason="Invalid credentials",
                customer_id=user.customer_id if user else None
            )
            return None
            
        self.audit_service.log_login_success(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            method="password"
        )
        return user

    async def create_session(
        self,
        user: User,
        device_info: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Create a new user session."""
        # Generate refresh token and JTI
        refresh_token = secrets.token_urlsafe(32)
        jti = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Create session
        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            jti=jti
        )
        
        self.db.add(session)
        self.db.commit()
        
        # Log session creation
        self.audit_service.log_session_creation(
            user=user,
            ip_address=ip_address or "",
            user_agent=user_agent or "",
            session_id=str(session.id)
        )
        
        return session

    async def get_active_sessions(self, user: User) -> List[UserSession]:
        """Get all active sessions for a user."""
        return self.db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).all()

    async def invalidate_session(self, session_id: str, reason: str = "user_logout") -> bool:
        """Invalidate a specific session."""
        session = self.db.query(UserSession).filter(UserSession.id == session_id).first()
        if not session:
            return False
            
        session.is_active = False
        self.db.commit()
        
        # Log session invalidation
        self.audit_service.log_session_invalidation(
            user=session.user,
            ip_address=session.ip_address or "",
            user_agent=session.user_agent or "",
            session_id=str(session.id),
            reason=reason
        )
        
        return True

    async def invalidate_all_sessions(self, user: User, reason: str = "user_request") -> None:
        """Invalidate all sessions for a user."""
        sessions = self.db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).all()
        
        for session in sessions:
            session.is_active = False
            # Log each session invalidation
            self.audit_service.log_session_invalidation(
                user=user,
                ip_address=session.ip_address or "",
                user_agent=session.user_agent or "",
                session_id=str(session.id),
                reason=reason
            )
            
        self.db.commit()

    async def refresh_session(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh a session using refresh token."""
        session = self.db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
            
        # Update session
        session.last_activity = datetime.utcnow()
        session.expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.db.commit()
        
        # Create new access token with session's JTI
        access_token = create_access_token(session.user_id, jti=session.jti)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": session.refresh_token
        }

    async def create_access_token(self, user: User, session: Optional[UserSession] = None) -> Dict[str, str]:
        """Create access token for authenticated user."""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Use session's JTI if available, otherwise generate new one
        jti = session.jti if session else None
        
        return {
            "access_token": create_access_token(
                user.id,
                expires_delta=access_token_expires,
                jti=jti
            ),
            "token_type": "bearer",
        }

    async def setup_mfa(self, user: User) -> Dict[str, Any]:
        """Setup MFA for a user."""
        # Generate secret key
        secret = pyotp.random_base32()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4) for _ in range(settings.MFA_BACKUP_CODES_COUNT)]
        
        # Create MFA settings
        mfa_settings = MFASettings(
            user_id=user.id,
            is_enabled=False,
            secret_key=secret,
            backup_codes=backup_codes
        )
        self.db.add(mfa_settings)
        self.db.commit()
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            user.email,
            issuer_name=settings.MFA_ISSUER
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to base64
        buffered = io.BytesIO()
        qr_image.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "secret_key": secret,
            "qr_code": qr_base64,
            "backup_codes": backup_codes
        }

    async def verify_mfa(self, user: User, code: str, ip_address: str, user_agent: str) -> bool:
        """Verify MFA code for a user."""
        mfa_settings = self.db.query(MFASettings).filter(
            MFASettings.user_id == user.id
        ).first()
        
        if not mfa_settings or not mfa_settings.is_enabled:
            self.audit_service.log_mfa_verification(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                method="totp",
                success=False
            )
            return False
            
        # Check if code is a backup code
        if code in mfa_settings.backup_codes:
            mfa_settings.backup_codes.remove(code)
            self.db.commit()
            self.audit_service.log_mfa_verification(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                method="backup_code",
                success=True
            )
            return True
            
        # Verify TOTP code
        totp = pyotp.TOTP(mfa_settings.secret_key)
        success = totp.verify(code)
        
        self.audit_service.log_mfa_verification(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            method="totp",
            success=success
        )
        
        return success

    async def enable_mfa(self, user: User, code: str) -> bool:
        """Enable MFA for a user after verification."""
        if not await self.verify_mfa(user, code, "", ""):
            return False
            
        mfa_settings = self.db.query(MFASettings).filter(
            MFASettings.user_id == user.id
        ).first()
        
        if not mfa_settings:
            return False
            
        mfa_settings.is_enabled = True
        self.db.commit()
        return True

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
        ip_address: str,
        user_agent: str
    ) -> bool:
        """Change user's password with validation."""
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            return False
            
        # Validate new password complexity
        self.validate_password_complexity(new_password)
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        
        # Log password change
        self.audit_service.log_password_change(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            method="user_initiated"
        )
        
        return True 