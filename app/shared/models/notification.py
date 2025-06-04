from sqlalchemy import Column, String, ForeignKey, Text, Boolean, JSON, Integer, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from app.shared.models.base import BaseModel
import enum
from datetime import datetime
import uuid

class NotificationType(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

class NotificationStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class Notification(BaseModel):
    __tablename__ = "notifications"
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(String(36), ForeignKey('users.id'))
    customer_id = Column(String(36), ForeignKey('customers.id'))
    type = Column(Enum(NotificationType))
    status = Column(Enum(NotificationStatus))
    title = Column(String)
    content = Column(Text)
    model_metadata = Column(JSON)  # Additional notification metadata
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    
    user = relationship("User", back_populates="notifications")
    customer = relationship("Customer")

class NotificationPreference(BaseModel):
    __tablename__ = "notification_preferences"
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(String(36), ForeignKey('users.id'))
    customer_id = Column(String(36), ForeignKey('customers.id'))
    type = Column(Enum(NotificationType))
    is_enabled = Column(Boolean, default=True)
    model_metadata = Column(JSON)  # Additional preference settings
    
    user = relationship("User", back_populates="notification_preferences")
    customer = relationship("Customer") 