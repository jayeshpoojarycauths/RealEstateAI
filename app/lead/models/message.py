import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.shared.db.base_class import BaseModel

class Message(BaseModel):
    """Message model for storing communication messages."""
    __tablename__ = "messages"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=True)
    subject = Column(String(200))
    content = Column(Text, nullable=False)
    message_type = Column(String(50), nullable=False)  # email, sms, etc.
    status = Column(String(50), default="pending")  # pending, sent, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    
    # Relationships
    customer = relationship("Customer", back_populates="messages")
    lead = relationship("Lead", back_populates="messages")
    interactions = relationship("MessageInteraction", back_populates="message", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Message {self.id}>"

class MessageInteraction(BaseModel):
    """Message interaction model for tracking message interactions."""
    __tablename__ = "message_interactions"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # open, click, reply, etc.
    interaction_data = Column(Text)  # Additional interaction data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message = relationship("Message", back_populates="interactions")

    def __repr__(self):
        return f"<MessageInteraction {self.id}>"

__all__ = ["Message", "MessageInteraction"] 