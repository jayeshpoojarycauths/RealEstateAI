from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, JSON, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.shared.db.base_class import Base

class OutreachChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"

class OutreachStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"

class OutreachLog(Base):
    __tablename__ = "outreach_logs"

    id = Column(UUID(as_uuid=True), primary_key=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    channel = Column(SQLEnum(OutreachChannel), nullable=False)
    status = Column(SQLEnum(OutreachStatus), nullable=False)
    message = Column(String)
    error_message = Column(String)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    last_retry_at = Column(DateTime)

class OutreachTemplate(Base):
    __tablename__ = "outreach_templates"
    __table_args__ = {'extend_existing': True}
    
    customer_id = Column(String(36), ForeignKey('customers.id'))
    name = Column(String)
    description = Column(Text)
    content = Column(Text)
    outreach_type = Column(Enum(OutreachType))
    is_active = Column(Boolean, default=True)
    model_metadata = Column(JSON)  # Additional template metadata
    
    customer = relationship("Customer")

class OutreachType(Enum):
    CALL = "call"
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"

class CommunicationPreferences(Base):
    __tablename__ = "communication_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    default_channel = Column(SQLEnum(OutreachChannel), nullable=False)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=True)
    whatsapp_enabled = Column(Boolean, default=True)
    preferences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 