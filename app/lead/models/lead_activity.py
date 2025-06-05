from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Integer, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.shared.db.base_class import BaseModel
from app.lead.models.lead import ActivityType
from sqlalchemy.dialects.postgresql import UUID

class LeadActivity(BaseModel):
    __tablename__ = "lead_activities"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    activity_type = Column(Enum(ActivityType), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    scheduled_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    model_metadata = Column(JSON)

    # Relationships
    lead = relationship("Lead", back_populates="activities")
    user = relationship("User", back_populates="lead_activities")

    def __repr__(self):
        return f"<LeadActivity {self.activity_type} for lead {self.lead_id}>" 