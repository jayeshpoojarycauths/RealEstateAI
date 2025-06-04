from sqlalchemy import Column, String, ForeignKey, Text, Boolean, JSON, Integer, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from app.shared.models.base import BaseModel
import enum
from datetime import datetime
import uuid

class OutreachStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OutreachType(enum.Enum):
    CALL = "call"
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"

class OutreachLog(BaseModel):
    __tablename__ = "outreach_logs"
    __table_args__ = {'extend_existing': True}
    
    lead_id = Column(String(36), ForeignKey('leads.id'))
    customer_id = Column(String(36), ForeignKey('customers.id'))
    outreach_type = Column(Enum(OutreachType))
    status = Column(Enum(OutreachStatus))
    scheduled_time = Column(DateTime)
    completed_time = Column(DateTime)
    response_time = Column(Float)  # Time to respond in seconds
    error_message = Column(Text)
    model_metadata = Column(JSON)  # Additional metadata about the outreach
    
    lead = relationship("Lead", back_populates="outreach_logs")
    customer = relationship("Customer")

class OutreachTemplate(BaseModel):
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