import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.db.base_class import BaseModel
from sqlalchemy.orm import Session
from app.shared.models.user import User
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.shared.models.user import User
from datetime import datetime
from sqlalchemy import func


class MFASettings(BaseModel):
    __tablename__ = "mfa_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    is_enabled = Column(Boolean, default=False)
    secret_key = Column(String)  # For TOTP
    backup_codes = Column(JSON)  # Backup codes for account recovery
    phone_number = Column(String)  # For SMS-based 2FA
    email = Column(String)  # For email-based 2FA
    preferred_method = Column(String, default="totp")  # totp, sms, email
    last_used = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="mfa_settings")

class UserSession(BaseModel):
    __tablename__ = "user_sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    refresh_token = Column(String, unique=True, nullable=False)
    jti = Column(String, unique=True, nullable=False)  # JWT ID for token tracking
    device_info = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class LoginAttempt(BaseModel):
    __tablename__ = "login_attempts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # Nullable for failed attempts
    email = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    user_agent = Column(String)
    success = Column(Boolean, default=False)
    attempt_time = Column(DateTime, default=datetime.utcnow)
    failure_reason = Column(String)

    # Relationships
    user = relationship("User", back_populates="login_attempts")

class PasswordReset(BaseModel):
    __tablename__ = "password_resets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="password_resets")

__all__ = ["MFASettings", "UserSession", "LoginAttempt", "PasswordReset"] 