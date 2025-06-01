"""
Consolidated models file containing all database models.
This file replaces the separate user.py and tenant.py files.
"""
from sqlalchemy import Column, String, ForeignKey, Table, Text, Boolean, JSON, Integer, Float, ARRAY, DateTime, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum
from sqlalchemy.sql import func
from datetime import datetime
import uuid

# Association tables
role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id')),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id')),
    extend_existing=True
)

user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id')),
    extend_existing=True
)

class InteractionType(enum.Enum):
    CALL = "call"
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"

class InteractionStatus(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    NO_RESPONSE = "no_response"

class CommunicationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    CALL = "call"
    VOICE = "voice"
    PHONE = "phone"
    PUSH = "push"

class OutreachChannel(str, enum.Enum):
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    VOICE = "voice"

class OutreachStatus(str, enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class Customer(BaseModel):
    __tablename__ = "customers"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="customer")
    roles = relationship("Role", back_populates="customer")
    communication_preferences = relationship("CommunicationPreferences", back_populates="customer", uselist=False)
    scraping_config = relationship("ScrapingConfig", back_populates="customer", uselist=False)
    refresh_tokens = relationship("RefreshToken", back_populates="customer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    leads = relationship("Lead", back_populates="customer")
    projects = relationship("Project", back_populates="customer")
    outreach = relationship("Outreach", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.name}>"

class User(BaseModel):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=True)  # Initially nullable
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    customer = relationship("Customer", back_populates="users")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    login_attempts = relationship("LoginAttempt", back_populates="user")
    mfa_settings = relationship("MFASettings", back_populates="user", uselist=False)
    password_resets = relationship("PasswordReset", back_populates="user")
    assigned_leads = relationship(
        "Lead",
        back_populates="assigned_user",
        foreign_keys="Lead.assigned_to"
    )
    lead_activities = relationship("LeadActivity", back_populates="user")
    user_communication_preferences = relationship("UserCommunicationPreference", back_populates="user")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

class Role(BaseModel):
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}
    
    name = Column(String, nullable=False)
    description = Column(Text)
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(BaseModel):
    __tablename__ = "permissions"
    __table_args__ = {'extend_existing': True}
    
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class Lead(BaseModel):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    source = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default="new")
    notes = Column(Text, nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    customer = relationship("Customer", back_populates="leads")
    assigned_user = relationship(
        "User",
        back_populates="assigned_leads",
        foreign_keys=[assigned_to]
    )
    created_by_user = relationship(
        "User",
        foreign_keys=[created_by]
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by]
    )
    activities = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    outreach = relationship("Outreach", back_populates="lead")
    projects = relationship("ProjectLead", back_populates="lead")
    score = relationship("LeadScore", back_populates="lead", uselist=False)
    interactions = relationship("InteractionLog", back_populates="lead")

    def __repr__(self):
        return f"<Lead(id={self.id}, name={self.name}, status={self.status})>"

class RealEstateProject(BaseModel):
    __tablename__ = "real_estate_projects"
    __table_args__ = {'extend_existing': True}
    
    name = Column(String, nullable=False)
    price = Column(String)
    size = Column(String)
    type = Column(String)
    builder = Column(String)
    location = Column(String)
    completion_date = Column(String)
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    customer = relationship("Customer")

class RealEstateBuyer(BaseModel):
    __tablename__ = "real_estate_buyers"
    __table_args__ = {'extend_existing': True}
    
    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    location = Column(String)
    budget = Column(String)
    property_type = Column(String)
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    customer = relationship("Customer")

class OutreachLog(BaseModel):
    __tablename__ = "outreach_logs"
    __table_args__ = {'extend_existing': True}
    
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'))
    channel = Column(String, nullable=False)  # SMS, Email, WhatsApp, etc.
    status = Column(String, nullable=False)
    message = Column(Text)
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    customer = relationship("Customer")
    lead = relationship("Lead")

class CommunicationPreferences(BaseModel):
    __tablename__ = "communication_preferences"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    whatsapp_enabled = Column(Boolean, default=True)
    telegram_enabled = Column(Boolean, default=True)
    email_frequency = Column(String(20), default="daily")  # daily, weekly, monthly
    sms_frequency = Column(String(20), default="daily")
    push_frequency = Column(String(20), default="daily")
    quiet_hours_start = Column(String(5), default="22:00")  # 24-hour format
    quiet_hours_end = Column(String(5), default="08:00")
    timezone = Column(String(50), default="UTC")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="communication_preferences")
    
    def __repr__(self):
        return f"<CommunicationPreferences(customer_id={self.customer_id})>"

class ScrapingConfig(BaseModel):
    __tablename__ = "scraping_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    magicbricks_enabled = Column(Boolean, default=True)
    ninety_nine_acres_enabled = Column(Boolean, default=True)
    scraping_interval = Column(Integer, default=24)  # in hours
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="scraping_config")
    
    def __repr__(self):
        return f"<ScrapingConfig {self.customer_id}>"

class LeadScore(BaseModel):
    __tablename__ = "lead_scores"
    __table_args__ = {'extend_existing': True}
    
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'))
    score = Column(Float, default=0.0)
    last_updated = Column(DateTime)
    scoring_factors = Column(JSON)  # Store factors that contributed to the score
    
    lead = relationship("Lead", back_populates="score")

class InteractionLog(BaseModel):
    __tablename__ = "interaction_logs"
    __table_args__ = {'extend_existing': True}
    
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'))
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    interaction_type = Column(Enum(InteractionType))
    status = Column(Enum(InteractionStatus))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)  # Duration in seconds
    user_input = Column(JSON)  # Store user inputs/choices
    error_message = Column(Text)
    response_time = Column(Float)  # Average response time in seconds
    
    lead = relationship("Lead", back_populates="interactions")
    customer = relationship("Customer")

class CallInteraction(BaseModel):
    __tablename__ = "call_interactions"
    __table_args__ = {'extend_existing': True}
    
    interaction_id = Column(UUID(as_uuid=True), ForeignKey('interaction_logs.id'))
    call_sid = Column(String)  # Twilio Call SID
    recording_url = Column(String)
    transcript = Column(Text)
    keypad_inputs = Column(JSON)  # Store keypad inputs
    menu_selections = Column(JSON)  # Store menu selections
    call_quality_metrics = Column(JSON)  # Store call quality metrics
    
    interaction = relationship("InteractionLog")

class MessageInteraction(BaseModel):
    __tablename__ = "message_interactions"
    __table_args__ = {'extend_existing': True}
    
    interaction_id = Column(UUID(as_uuid=True), ForeignKey('interaction_logs.id'))
    message_id = Column(String)  # Provider's message ID
    content = Column(Text)
    response_content = Column(Text)
    response_time = Column(Integer)  # Time to respond in seconds
    delivery_status = Column(String)
    
    interaction = relationship("InteractionLog")

class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(255), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)
    device_info = Column(Text, nullable=True)  # Store device info for remember me

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    customer = relationship("Customer", back_populates="refresh_tokens")

    def is_valid(self):
        return not self.is_revoked and datetime.utcnow() < self.expires_at

class LoginAttempt(BaseModel):
    __tablename__ = "login_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Nullable for failed attempts
    email = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    user_agent = Column(String)
    success = Column(Boolean, default=False)
    attempt_time = Column(DateTime, default=datetime.utcnow)
    failure_reason = Column(String)

    # Relationships
    user = relationship("User", back_populates="login_attempts")

class MFASettings(BaseModel):
    __tablename__ = "mfa_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    is_enabled = Column(Boolean, default=False)
    secret_key = Column(String)  # For TOTP
    backup_codes = Column(ARRAY(String))  # Backup codes for account recovery
    phone_number = Column(String)  # For SMS-based 2FA
    email = Column(String)  # For email-based 2FA
    preferred_method = Column(String, default="totp")  # totp, sms, email
    last_used = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="mfa_settings")

class PasswordReset(BaseModel):
    __tablename__ = "password_resets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="password_resets")

class UserCommunicationPreference(BaseModel):
    __tablename__ = "user_communication_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    communication_preferences_id = Column(Integer, ForeignKey("communication_preferences.id"), nullable=False)
    channel = Column(Enum(CommunicationChannel), nullable=False)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="user_communication_preferences")
    communication_preferences = relationship("CommunicationPreferences")

    def __repr__(self):
        return f"<UserCommunicationPreference {self.channel} for user {self.user_id}>"

class ActivityType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    SMS = "sms"
    MEETING = "meeting"
    NOTE = "note"
    STATUS_CHANGE = "status_change"
    ASSIGNMENT = "assignment"
    OTHER = "other"

class LeadActivity(BaseModel):
    __tablename__ = "lead_activities"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    activity_type = Column(Enum(ActivityType), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    lead = relationship("Lead", back_populates="activities")
    user = relationship("User", back_populates="lead_activities")

    def __repr__(self):
        return f"<LeadActivity(id={self.id}, type={self.activity_type}, lead_id={self.lead_id})>" 

class Project(BaseModel):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String, nullable=False)
    price_range = Column(String)
    status = Column(Enum(ProjectStatus, values_callable=lambda x: [e.value for e in x]), default=ProjectStatus.PLANNING)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    customer = relationship("Customer", back_populates="projects")
    leads = relationship("ProjectLead", back_populates="project")

    def __repr__(self):
        return f"<Project {self.name}>"

class Outreach(BaseModel):
    __tablename__ = "outreach"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(String(36), ForeignKey("leads.id"))
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    channel = Column(Enum(OutreachChannel), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(OutreachStatus), default=OutreachStatus.PENDING)
    outreach_metadata = Column(JSON)  # Renamed from metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    lead = relationship("Lead", back_populates="outreach")
    customer = relationship("Customer", back_populates="outreach")

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    details = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="audit_logs")
    customer = relationship("Customer", backref="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, entity_type={self.entity_type})>" 

class ProjectLead(BaseModel):
    __tablename__ = "project_leads"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    status = Column(String, nullable=False, default="active")
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    
    # Relationships
    project = relationship("Project", back_populates="leads")
    lead = relationship("Lead", back_populates="projects")
    assigner = relationship("User", foreign_keys=[assigned_by])
    
    __table_args__ = (
        UniqueConstraint('project_id', 'lead_id', name='uix_project_lead'),
    )

    def __repr__(self):
        return f"<ProjectLead(id={self.id}, project_id={self.project_id}, lead_id={self.lead_id})>" 

class ScrapedLead(BaseModel):
    __tablename__ = 'scraped_leads'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customer.id'), nullable=False)
    lead_type = Column(String, nullable=False)  # 'user', 'property', 'location', etc.
    data = Column(JSONB, nullable=False)  # Store scraped data as JSON
    source = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 

class UserSession(BaseModel):
    __tablename__ = "user_sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
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