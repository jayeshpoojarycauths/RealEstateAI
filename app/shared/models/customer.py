from typing import TYPE_CHECKING
import uuid
from sqlalchemy import (JSON, Boolean, Column, String, Text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.shared.db.base_class import BaseModel

if TYPE_CHECKING:
    from app.shared.models.user import User
    from app.project.models.project import Project

class Customer(BaseModel):
    """Customer model representing a client organization."""
    __tablename__ = "customers"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    # TODO: Add RealEstateProject relationship when implemented
    audit_logs = relationship("AuditLog", back_populates="customer", foreign_keys="[AuditLog.customer_id]")
    outreach_templates = relationship("OutreachTemplate", back_populates="customer")
    notifications = relationship("Notification", back_populates="customer")
    notification_preferences = relationship("NotificationPreference", back_populates="customer")
    scraping_config = relationship("ScrapingConfig", back_populates="customer", uselist=False)

    def __repr__(self):
        return f"<Customer {self.name}>"
