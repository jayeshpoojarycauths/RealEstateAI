"""
Audit log model for tracking system events.
"""

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.shared.db.base_class import Base

class AuditLog(Base):
    """Audit log model for tracking system events."""
    __tablename__ = "audit_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    details = Column(JSON)
    timestamp = Column(DateTime, nullable=False)
    
    # Use string references for relationships
    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])
    customer = relationship("Customer", back_populates="audit_logs", foreign_keys=[customer_id])

__all__ = ["AuditLog"] 