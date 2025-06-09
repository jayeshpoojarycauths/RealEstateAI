import enum

from sqlalchemy import (JSON, Column, DateTime, Enum, Float,
                        ForeignKey, Integer, String, Text)
from sqlalchemy.orm import relationship

from app.shared.db.base_class import Base

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

class InteractionLog(Base):
    __tablename__ = "interaction_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, index=True)
    lead_id = Column(String(36), ForeignKey('leads.id'))
    customer_id = Column(String(36), ForeignKey('customers.id'))
    interaction_type = Column(Enum(InteractionType))
    status = Column(Enum(InteractionStatus))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)  # Duration in seconds
    user_input = Column(JSON)  # Store user inputs/choices
    error_message = Column(Text)
    response_time = Column(Float)  # Average response time in seconds
    model_metadata = Column(JSON)  # Additional interaction metadata
    
    # Use string references for relationships
    lead = relationship("Lead", back_populates="interactions", foreign_keys=[lead_id])
    customer = relationship("Customer", foreign_keys=[customer_id])

class CallInteraction(Base):
    __tablename__ = "call_interactions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, index=True)
    interaction_id = Column(String(36), ForeignKey('interaction_logs.id'))
    call_sid = Column(String)  # Twilio Call SID
    recording_url = Column(String)
    transcript = Column(Text)
    keypad_inputs = Column(JSON)  # Store keypad inputs
    menu_selections = Column(JSON)  # Store menu selections
    call_quality_metrics = Column(JSON)  # Store call quality metrics
    model_metadata = Column(JSON)  # Additional call metadata
    
    interaction = relationship("InteractionLog")

class MessageInteraction(Base):
    __tablename__ = "message_interactions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, index=True)
    interaction_id = Column(String(36), ForeignKey('interaction_logs.id'))
    message_id = Column(String)  # Provider's message ID
    content = Column(Text)
    response_content = Column(Text)
    response_time = Column(Integer)  # Time to respond in seconds
    delivery_status = Column(String)
    model_metadata = Column(JSON)  # Additional message metadata
    
    interaction = relationship("InteractionLog")

__all__ = [
    "InteractionType",
    "InteractionStatus",
    "CommunicationChannel",
    "InteractionLog",
    "CallInteraction",
    "MessageInteraction"
] 