from sqlalchemy import Column, String, Boolean, ForeignKey, Table, Integer, Text, JSON, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from app.shared.models.base import BaseModel
import enum
from datetime import datetime
import uuid

# Association tables
user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    CUSTOMER = "customer"

class User(BaseModel):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    customer_id = Column(String(36), ForeignKey('customers.id'))
    last_login = Column(DateTime)
    model_metadata = Column(JSON)  # Additional user metadata
    
    # Relationships
    customer = relationship("Customer", back_populates="users")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    notification_preferences = relationship("NotificationPreference", back_populates="user")
    mfa_settings = relationship("MFASettings", back_populates="user", uselist=False)
    login_attempts = relationship("LoginAttempt", back_populates="user")
    password_resets = relationship("PasswordReset", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")

class Role(BaseModel):
    """Role model for role-based access control."""
    __tablename__ = "roles"

    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    
    # Relationships
    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

class Permission(BaseModel):
    """Permission model for fine-grained access control."""
    __tablename__ = "permissions"

    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    
    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions") 