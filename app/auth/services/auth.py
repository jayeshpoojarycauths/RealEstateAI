import base64
import io
import json
import re
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pyotp
import qrcode
from sqlalchemy.orm import Session

from app.auth.models.auth import (MFASettings, UserSession)
from app.shared.core.audit import AuditService
from app.shared.core.config import settings
from app.shared.core.email import (send_password_reset_email,
                                   send_verification_email)
from app.shared.core.exceptions import (ValidationException)
from app.shared.core.security import (create_access_token,
                                      create_refresh_token, decrypt_value,
                                      encrypt_value, get_password_hash,
                                      hash_code, verify_jwt_token,
                                      verify_mfa_code, verify_password)
from app.shared.core.security.roles import Role
from app.shared.models.user import User
from app.shared.schemas.auth import (UserCreate)
from app.shared.schemas.user import UserUpdate
from fastapi import Request
from sqlalchemy.orm import Session
from app.shared.models.user import User
from datetime import datetime
from typing import Dict
from typing import Any
from datetime import timedelta
from fastapi import Request
from sqlalchemy.orm import Session
from app.shared.models.user import User
from datetime import datetime
from typing import Dict
from typing import Any
from datetime import timedelta


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def validate_password_complexity(self, password: str) -> None:
        """Validate password complexity requirements."""
        if len(password) < 8:
            raise ValidationException(detail="Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', password):
            raise ValidationException(detail="Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValidationException(detail="Password must contain at least one lowercase letter")
        if not re.search(r'\d', password):
            raise ValidationException(detail="Password must contain at least one number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationException(detail="Password must contain at least one special character")

    async def authenticate(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user.
        """
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def register(self, user_in: UserCreate) -> User:
        """
        Register a new user.
        """
        # Check if user exists
        user = self.db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise ValidationException("Email already registered")

        # Create user
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            role=user_in.role or Role.GUEST,
            is_active=True,
            is_superuser=False,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Send verification email
        await send_verification_email(
            email_to=user.email,
            token=create_access_token(user.id),
            user_name=user.full_name
        )

        return user

    async def request_password_reset(self, email: str) -> None:
        """
        Request a password reset.
        """
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return

        # Generate reset token
        token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
        )

        # Send reset email
        await send_password_reset_email(
            email_to=user.email,
            token=token,
            user_name=user.full_name
        )

    async def confirm_password_reset(
        self,
        token: str,
        new_password: str
    ) -> None:
        """
        Confirm password reset.
        """
        try:
            # Verify token
            payload = verify_jwt_token(token)
            user_id = payload.get("sub")
            if not user_id:
                raise ValidationException("Invalid token")

            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValidationException("User not found")

            # Update password
            user.hashed_password = get_password_hash(new_password)
            self.db.commit()

        except Exception as e:
            raise ValidationException(str(e))

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
                success=False,
                reason="MFA not enabled"
            )
            return False

        # Verify code
        if not verify_mfa_code(code, mfa_settings.secret_key):
            self.audit_service.log_mfa_verification(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                reason="Invalid code"
            )
            return False

        self.audit_service.log_mfa_verification(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )
        return True

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
            UserSession.is_active,
            UserSession.expires_at > datetime.utcnow()
        ).all()

    async def invalidate_session(self, session_id: str) -> None:
        """Invalidate a session."""
        session = self.db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.is_active
        ).first()
        if session:
            session.is_active = False
            self.db.commit()

    async def invalidate_all_sessions(self, user_id: str) -> None:
        """Invalidate all sessions for a user."""
        self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active
        ).update({"is_active": False})
        self.db.commit()

    async def refresh_session(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh a session."""
        session = await self.get_session_by_token(refresh_token)
        if not session or not session.is_active:
            return None

        if session.expires_at < datetime.utcnow():
            session.is_active = False
            self.db.commit()
            return None

        # Create new access token
        access_token = create_access_token(session.user_id)
        return {
            "access_token": access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer"
        }

    async def create_access_token(self, user: User, session: Optional[UserSession] = None) -> Dict[str, str]:
        """Create access and refresh tokens for a user."""
        access_token = create_access_token(user.id)
        if not session:
            session = await self.create_session(user)
        return {
            "access_token": access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer"
        }

    async def setup_mfa(self, user: User) -> Dict[str, Any]:
        """Set up MFA for a user."""
        # Generate secret key
        secret_key = pyotp.random_base32()
        
        # Create TOTP object
        totp = pyotp.TOTP(secret_key)
        
        # Generate provisioning URI
        provisioning_uri = totp.provisioning_uri(
            user.email,
            issuer_name=settings.PROJECT_NAME
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_code = base64.b64encode(buffered.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [secrets.token_urlsafe(4) for _ in range(8)]
        hashed_backup_codes = [hash_code(code) for code in backup_codes]
        
        # Store MFA settings
        mfa_settings = MFASettings(
            user_id=user.id,
            secret_key=encrypt_value(secret_key),
            backup_codes=json.dumps(hashed_backup_codes),
            is_enabled=False
        )
        self.db.add(mfa_settings)
        self.db.commit()
        
        return {
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "secret_key": secret_key
        }

    async def enable_mfa(self, user: User, code: str) -> bool:
        """Enable MFA for a user."""
        mfa_settings = self.db.query(MFASettings).filter(
            MFASettings.user_id == user.id
        ).first()
        
        if not mfa_settings:
            return False
            
        secret_key = decrypt_value(mfa_settings.secret_key)
        if not verify_mfa_code(code, secret_key):
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
        """Change a user's password."""
        if not verify_password(current_password, user.hashed_password):
            self.audit_service.log_password_change(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                reason="Invalid current password"
            )
            return False
            
        # Validate new password
        self.validate_password_complexity(new_password)
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        
        # Log successful change
        self.audit_service.log_password_change(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )
        
        return True

    async def get_session_by_token(self, refresh_token: str) -> Optional[UserSession]:
        """Get a session by refresh token."""
        return self.db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active
        ).first()

    def update_user(self, user: User, user_in: UserUpdate) -> User:
        """Update a user."""
        for field, value in user_in.dict(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[Role] = None,
    ) -> list[User]:
        """Get users with optional filtering."""
        query = self.db.query(User)
        if role:
            query = query.filter(User.role == role)
        return query.offset(skip).limit(limit).all()

    def create_tokens(self, user: User) -> dict:
        """Create access and refresh tokens for a user."""
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        } 