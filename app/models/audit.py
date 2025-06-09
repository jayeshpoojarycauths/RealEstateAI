import uuid

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.shared.db.base_class import Base
from app.shared.models.user import User
from app.shared.models.user import User


class AuditLog(Base):
    __tablename__ = "audit_logs"

    # Note: This model previously used Integer for IDs. Migration needed to change to UUID.
    # TODO: Create migration to change id, tenant_id, resource_id, and user_id to UUID type
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    action = Column(String, nullable=False)  # e.g., 'create', 'update', 'delete'
    resource_type = Column(String, nullable=False)  # e.g., 'lead', 'project', 'outreach'
    resource_id = Column(UUID(as_uuid=True), nullable=False)
    details = Column(JSON, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id} at {self.timestamp}>" 