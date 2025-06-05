from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum, JSON, Float, UUID, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.shared.db.base_class import BaseModel
import uuid
from datetime import datetime
import enum

class ActivityType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    SMS = "sms"
    MEETING = "meeting"
    NOTE = "note"
    STATUS_CHANGE = "status_change"
    ASSIGNMENT = "assignment"
    OTHER = "other"

class LeadSource(str, enum.Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL = "social"
    DIRECT = "direct"
    OTHER = "other"

class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED = "closed"
    LOST = "lost"

class Lead(BaseModel):
    __tablename__ = "leads"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    source = Column(Enum(LeadSource), default=LeadSource.OTHER)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    notes = Column(Text, nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    budget = Column(Float)
    last_contacted_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    model_metadata = Column(JSON)
    
    # Relationships
    customer = relationship("Customer", back_populates="leads")
    assigned_user = relationship(
        "User",
        back_populates="assigned_leads",
        foreign_keys=[assigned_to]
    )
    created_by_user = relationship(
        "User",
        foreign_keys=[created_by]
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by]
    )
    activities = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    outreach = relationship("Outreach", back_populates="lead")
    projects = relationship("Project", secondary="project_leads", back_populates="leads")
    real_estate_projects = relationship("RealEstateProject", secondary="project_leads", back_populates="leads")
    score = relationship("LeadScore", back_populates="lead", uselist=False)
    interactions = relationship("InteractionLog", back_populates="lead")
    outreach_logs = relationship("OutreachLog", back_populates="lead")

    def __repr__(self):
        return f"<Lead {self.name}>"

class LeadScore(BaseModel):
    __tablename__ = "lead_scores"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'))
    score = Column(Float, default=0.0)
    last_updated = Column(DateTime)
    scoring_factors = Column(JSON)  # Store factors that contributed to the score
    
    lead = relationship("Lead", back_populates="score")

class LeadActivity(BaseModel):
    __tablename__ = "lead_activities"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
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