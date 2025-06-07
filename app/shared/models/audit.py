from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.shared.models.base import BaseModel
from app.shared.models.customer import Customer

class AuditLog(BaseModel):
    """Audit log model for tracking system events."""
    __tablename__ = "audit_logs"

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    details = Column(JSON)
    timestamp = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    customer = relationship("Customer", back_populates="audit_logs") 