import enum
from datetime import datetime

from sqlalchemy import (JSON, Boolean, Column, DateTime, Enum, Float,
                        ForeignKey, Integer, String, Table, Text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.db.base_class import BaseModel
from app.shared.models.user import User
from app.lead.models.lead_types import ActivityType
from app.shared.models.associations import project_leads

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
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    company = Column(String(255))
    source = Column(Enum(LeadSource), default=LeadSource.OTHER)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    notes = Column(Text, nullable=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    updated_by = Column(String(36), ForeignKey("users.id"), nullable=True)
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
    activities = relationship("app.lead.models.lead_activity.LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    projects = relationship("Project", secondary=project_leads, back_populates="leads")
    score = relationship("LeadScore", back_populates="lead", uselist=False)
    outreach_logs = relationship("OutreachLog", back_populates="lead")
    interactions = relationship("InteractionLog", back_populates="lead", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lead {self.name}>"

class LeadScore(BaseModel):
    __tablename__ = "lead_scores"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, index=True)
    lead_id = Column(String(36), ForeignKey('leads.id'))
    score = Column(Float, default=0.0)
    last_updated = Column(DateTime)
    scoring_factors = Column(JSON)  # Store factors that contributed to the score
    
    lead = relationship("Lead", back_populates="score") 