from sqlalchemy import Column, String, ForeignKey, Text, Boolean, JSON, Integer, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from app.shared.models.base import BaseModel
import enum
from datetime import datetime
import uuid

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

class InteractionLog(BaseModel):
    __tablename__ = "interaction_logs"
    __table_args__ = {'extend_existing': True}
    
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
    
    lead = relationship("Lead", back_populates="interactions")
    customer = relationship("Customer")

class CallInteraction(BaseModel):
    __tablename__ = "call_interactions"
    __table_args__ = {'extend_existing': True}
    
    interaction_id = Column(String(36), ForeignKey('interaction_logs.id'))
    call_sid = Column(String)  # Twilio Call SID
    recording_url = Column(String)
    transcript = Column(Text)
    keypad_inputs = Column(JSON)  # Store keypad inputs
    menu_selections = Column(JSON)  # Store menu selections
    call_quality_metrics = Column(JSON)  # Store call quality metrics
    model_metadata = Column(JSON)  # Additional call metadata
    
    interaction = relationship("InteractionLog")

class MessageInteraction(BaseModel):
    __tablename__ = "message_interactions"
    __table_args__ = {'extend_existing': True}
    
    interaction_id = Column(String(36), ForeignKey('interaction_logs.id'))
    message_id = Column(String)  # Provider's message ID
    content = Column(Text)
    response_content = Column(Text)
    response_time = Column(Integer)  # Time to respond in seconds
    delivery_status = Column(String)
    model_metadata = Column(JSON)  # Additional message metadata
    
    interaction = relationship("InteractionLog") 