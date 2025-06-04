from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship

from app.shared.db.base_class import Base
from app.shared.models.user import User

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="active")
    type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    created_by_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    features = relationship("ProjectFeature", back_populates="project", cascade="all, delete-orphan")
    images = relationship("ProjectImage", back_populates="project", cascade="all, delete-orphan")
    amenities = relationship("ProjectAmenity", back_populates="project", cascade="all, delete-orphan")
    leads = relationship("ProjectLead", back_populates="project", cascade="all, delete-orphan")

class ProjectFeature(Base):
    __tablename__ = "project_features"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Relationships
    project = relationship("Project", back_populates="features")

class ProjectImage(Base):
    __tablename__ = "project_images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    caption = Column(String(255))
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Relationships
    project = relationship("Project", back_populates="images")

class ProjectAmenity(Base):
    __tablename__ = "project_amenities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Relationships
    project = relationship("Project", back_populates="amenities")

class ProjectLead(Base):
    __tablename__ = "project_leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    status = Column(String(50), default="new")
    notes = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    project = relationship("Project", back_populates="leads")
    assigned_to = relationship("User") 