from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.shared.db.base_class import BaseModel
import uuid
from sqlalchemy.dialects.postgresql import UUID

class LeadActivity(BaseModel):
    __tablename__ = "lead_activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="activities")
    user = relationship("User")

    def __repr__(self):
        return f"<LeadActivity {self.activity_type} for lead {self.lead_id}>" 