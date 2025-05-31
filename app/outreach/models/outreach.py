from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.shared.db.base_class import Base
from app.schemas.outreach import OutreachChannel, OutreachStatus
from sqlalchemy.dialects.postgresql import UUID

class Outreach(Base):
    __tablename__ = "outreach"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    channel = Column(Enum(OutreachChannel), nullable=False)
    message = Column(Text, nullable=False)
    subject = Column(String(200))
    template_id = Column(String(100))
    variables = Column(JSON)
    status = Column(Enum(OutreachStatus), nullable=False, default=OutreachStatus.SCHEDULED)
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lead = relationship("Lead", back_populates="outreach")
    customer = relationship("Customer", back_populates="outreach")

class OutreachTemplate(Base):
    __tablename__ = "outreach_templates"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    channel = Column(Enum(OutreachChannel), nullable=False)
    subject = Column(String(200))
    body = Column(Text, nullable=False)
    variables = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="outreach_templates")

class OutreachChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"

class OutreachStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class OutreachLog(Base):
    __tablename__ = "outreach_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    channel = Column(Enum(OutreachChannel), nullable=False)
    status = Column(Enum(OutreachStatus), default=OutreachStatus.PENDING)
    message = Column(String, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="outreach_logs")
    lead = relationship("Lead", back_populates="outreach_logs") 