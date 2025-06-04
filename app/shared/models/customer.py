from sqlalchemy import Column, String, ForeignKey, Text, Boolean, JSON, Integer, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from app.shared.models.base import BaseModel
import enum
from datetime import datetime
import uuid

class Customer(BaseModel):
    """Customer model representing a client organization."""
    __tablename__ = "customers"
    __table_args__ = {'extend_existing': True}

    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    model_metadata = Column(JSON)  # Additional customer metadata
    
    # Relationships
    users = relationship("User", back_populates="customer")
    leads = relationship("Lead", back_populates="customer")
    projects = relationship("Project", back_populates="customer")
    real_estate_projects = relationship("RealEstateProject", back_populates="customer")
    audit_logs = relationship("AuditLog", back_populates="customer")
    refresh_tokens = relationship("RefreshToken", back_populates="customer")
    outreach_templates = relationship("OutreachTemplate", back_populates="customer")
    notifications = relationship("Notification", back_populates="customer")
    notification_preferences = relationship("NotificationPreference", back_populates="customer") 