from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Table)
from sqlalchemy.orm import relationship

from app.shared.core.security.role_types import Role
from app.shared.db.base_class import Base

if TYPE_CHECKING:
    from app.shared.models.customer import Customer
    from app.shared.models.notification import Notification, NotificationPreference

# Association tables
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class UserRole:
    """User role management."""
    
    def __init__(self, user: 'User'):
        self.user = user
    
    @property
    def is_admin(self) -> bool:
        return self.user.role == Role.ADMIN
    
    @property
    def is_agent(self) -> bool:
        return self.user.role == Role.AGENT
    
    @property
    def is_customer(self) -> bool:
        return self.user.role == Role.CUSTOMER
    
    @property
    def is_guest(self) -> bool:
        return self.user.role == Role.GUEST

class User(Base):
    """
    User model for storing user information.
    
    Attributes:
        id (str): Unique identifier for the user
        email (str): User's email address (unique)
        username (str): User's username (unique)
        password_hash (str): Hashed password
        first_name (str): User's first name
        last_name (str): User's last name
        is_active (bool): Whether the user is active
        is_superuser (bool): Whether the user is a superuser
        created_at (datetime): When the user was created
        updated_at (datetime): When the user was last updated
        reset_token (str): Reset token for password reset
        reset_token_expires (datetime): Expiration time for the reset token
    """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    last_login = Column(DateTime, nullable=True)
    model_metadata = Column(JSON, nullable=True)
    reset_token = Column(String, unique=True, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # Use string-based relationship references
    customer = relationship("Customer", back_populates="users", foreign_keys=[customer_id])
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    login_attempts = relationship("LoginAttempt", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    mfa_settings = relationship("MFASettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # App-specific relationships
    assigned_leads = relationship("Lead", back_populates="assigned_user", foreign_keys="[Lead.assigned_to]")
    created_leads = relationship("Lead", back_populates="created_by_user", foreign_keys="[Lead.created_by]")
    updated_leads = relationship("Lead", back_populates="updated_by_user", foreign_keys="[Lead.updated_by]")
    created_projects = relationship("Project", back_populates="created_by_user", foreign_keys="[Project.created_by_id]")
    updated_projects = relationship("Project", back_populates="updated_by_user", foreign_keys="[Project.updated_by_id]")
    assigned_projects = relationship("Project", back_populates="assigned_to", foreign_keys="[Project.assigned_to_id]")
    scraping_configs = relationship("ScrapingConfig", back_populates="user", cascade="all, delete-orphan")
    lead_activities = relationship("app.lead.models.lead_activity.LeadActivity", back_populates="user")
    
    # Relationships
    notifications = relationship("Notification", back_populates="user")
    notification_preferences = relationship("NotificationPreference", back_populates="user", uselist=False)
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user", foreign_keys="[AuditLog.user_id]")
    
    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == Role.ADMIN.value

    @property
    def is_agent(self) -> bool:
        """Check if user is an agent."""
        return self.role == Role.AGENT.value

    @property
    def is_customer(self) -> bool:
        """Check if user is a customer."""
        return self.role == Role.CUSTOMER.value

    @property
    def is_guest(self) -> bool:
        """Check if user is a guest."""
        return self.role == Role.GUEST.value

    def has_role(self, role: Role) -> bool:
        """Check if user has a specific role."""
        return self.role == role.value

    def has_any_role(self, *roles: Role) -> bool:
        """Check if user has any of the specified roles."""
        return any(self.has_role(role) for role in roles)

    def has_all_roles(self, *roles: Role) -> bool:
        """Check if user has all of the specified roles."""
        return all(self.has_role(role) for role in roles)

    def get_notification_preference(self) -> Optional["NotificationPreference"]:
        """Get user's notification preferences."""
        return self.notification_preferences

    def get_unread_notifications(self) -> list["Notification"]:
        """Get user's unread notifications."""
        return [n for n in self.notifications if not n.is_read]

    def get_recent_notifications(self, limit: int = 10) -> list["Notification"]:
        """Get user's most recent notifications."""
        return sorted(
            self.notifications,
            key=lambda x: x.created_at,
            reverse=True
        )[:limit]

class Role(Base):
    """Role model for role-based access control."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

    def __repr__(self):
        return f"<Role {self.name}>"

class Permission(Base):
    """Permission model for fine-grained access control."""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self):
        return f"<Permission {self.name}>"

__all__ = ["User", "Role", "Permission"] 