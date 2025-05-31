from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import User, Customer, MFASettings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings
import pyotp
import secrets
import qrcode
import io
import base64

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    async def create_access_token(self, user: User) -> Dict[str, str]:
        """Create access token for authenticated user."""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }

    async def setup_mfa(self, user: User) -> Dict[str, Any]:
        """Setup MFA for a user."""
        # Generate secret key
        secret = pyotp.random_base32()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4) for _ in range(8)]
        
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
            issuer_name=settings.PROJECT_NAME
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

    async def verify_mfa(self, user: User, code: str) -> bool:
        """Verify MFA code for a user."""
        mfa_settings = self.db.query(MFASettings).filter(
            MFASettings.user_id == user.id
        ).first()
        
        if not mfa_settings or not mfa_settings.is_enabled:
            return False
            
        # Check if code is a backup code
        if code in mfa_settings.backup_codes:
            mfa_settings.backup_codes.remove(code)
            self.db.commit()
            return True
            
        # Verify TOTP code
        totp = pyotp.TOTP(mfa_settings.secret_key)
        return totp.verify(code)

    async def enable_mfa(self, user: User, code: str) -> bool:
        """Enable MFA for a user after verification."""
        if not await self.verify_mfa(user, code):
            return False
            
        mfa_settings = self.db.query(MFASettings).filter(
            MFASettings.user_id == user.id
        ).first()
        
        if not mfa_settings:
            return False
            
        mfa_settings.is_enabled = True
        self.db.commit()
        return True 