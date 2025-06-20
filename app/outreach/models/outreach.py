import enum
import uuid

from sqlalchemy import (JSON, Boolean, Column, DateTime, Enum, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.db.base_class import BaseModel
from sqlalchemy import func
from sqlalchemy import func


class OutreachChannel(str, enum.Enum):
    """Communication channels for outreach."""
    EMAIL = "email"
    SMS = "sms"
    CALL = "call"
    WHATSAPP = "whatsapp"

class OutreachStatus(str, enum.Enum):
    """Status of outreach attempts."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Outreach(BaseModel):
    """Model for tracking outreach attempts."""
    __tablename__ = "outreach"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    channel = Column(Enum(OutreachChannel), nullable=False)
    message = Column(Text, nullable=False)
    subject = Column(String(200))
    template_id = Column(String(100))
    variables = Column(JSON)
    status = Column(Enum(OutreachStatus), nullable=False, default=OutreachStatus.PENDING)
    scheduled_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    lead = relationship("Lead")
    customer = relationship("Customer")
    
    def __repr__(self):
        return f"<Outreach {self.id} - {self.channel}>"

class OutreachTemplate(BaseModel):
    """Model for storing outreach message templates."""
    __tablename__ = "outreach_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    channel = Column(Enum(OutreachChannel), nullable=False)
    subject = Column(String(200))
    body = Column(Text, nullable=False)
    variables = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="outreach_templates")
    
    def __repr__(self):
        return f"<OutreachTemplate {self.name}>"

class OutreachLog(BaseModel):
    """Model for logging outreach activities."""
    __tablename__ = "outreach_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    channel = Column(Enum(OutreachChannel), nullable=False)
    status = Column(Enum(OutreachStatus), default=OutreachStatus.PENDING)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    lead = relationship("Lead")
    customer = relationship("Customer")
    
    def __repr__(self):
        return f"<OutreachLog {self.id} - {self.channel}>"

class CommunicationPreference(BaseModel):
    """Model for storing communication preferences."""
    __tablename__ = "communication_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    default_channel = Column(Enum(OutreachChannel), nullable=False)
    email_template = Column(String(100))
    sms_template = Column(String(100))
    whatsapp_template = Column(String(100))
    working_hours_start = Column(String(5))  # Format: "HH:MM"
    working_hours_end = Column(String(5))    # Format: "HH:MM"
    max_daily_outreach = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    
    def __repr__(self):
        return f"<CommunicationPreference {self.customer_id}>"

class OutreachCampaign(BaseModel):
    __tablename__ = "outreach_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    channel = Column(Enum(OutreachChannel), nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    total_recipients = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    campaign_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    customer = relationship("Customer")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<OutreachCampaign {self.id} - {self.name}>" 