from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Float, Boolean, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.shared.db.base_class import BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

class ProjectType(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"
    INDUSTRIAL = "industrial"
    OTHER = "other"

class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

# Association table for project leads
project_leads = Table(
    'project_leads',
    BaseModel.metadata,
    Column('project_id', String(36), ForeignKey('projects.id'), primary_key=True),
    Column('lead_id', String(36), ForeignKey('leads.id'), primary_key=True)
)

class Project(BaseModel):
    __tablename__ = "projects"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum(ProjectType), nullable=False)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNING)
    location = Column(String(200), nullable=False)
    total_units = Column(Integer)
    price_range = Column(String(100))
    amenities = Column(JSON)
    completion_date = Column(DateTime)
    total_value = Column(Float, default=0.0)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float)
    model_metadata = Column(JSON)  # Additional project metadata
    
    # Location fields
    address = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Foreign keys
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="projects")
    leads = relationship("Lead", secondary=project_leads, back_populates="projects")
    features = relationship("ProjectFeature", back_populates="project", cascade="all, delete-orphan")
    images = relationship("ProjectImage", back_populates="project", cascade="all, delete-orphan")
    amenities_list = relationship("ProjectAmenity", back_populates="project", cascade="all, delete-orphan")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<Project {self.name}>"

class ProjectFeature(BaseModel):
    __tablename__ = "project_features"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    value = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Relationships
    project = relationship("Project", back_populates="features")
    
    def __repr__(self):
        return f"<ProjectFeature {self.name}>"

class ProjectImage(BaseModel):
    __tablename__ = "project_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(500), nullable=False)
    caption = Column(String(200))
    is_primary = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    
    # Relationships
    project = relationship("Project", back_populates="images")
    
    def __repr__(self):
        return f"<ProjectImage {self.url}>"

class ProjectAmenity(BaseModel):
    __tablename__ = "project_amenities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    icon = Column(String(100))
    
    # Relationships
    project = relationship("Project", back_populates="amenities_list")
    
    def __repr__(self):
        return f"<ProjectAmenity {self.name}>"

class RealEstateProject(BaseModel):
    __tablename__ = "real_estate_projects"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(Text)
    location = Column(String)
    property_type = Column(String)
    total_units = Column(Integer)
    price_range_min = Column(Float)
    price_range_max = Column(Float)
    amenities = Column(JSON)  # List of amenities
    images = Column(JSON)  # List of image URLs
    status = Column(Enum(ProjectStatus))
    customer_id = Column(String(36), ForeignKey('customers.id'))
    start_date = Column(DateTime)
    completion_date = Column(DateTime)
    model_metadata = Column(JSON)  # Additional project metadata
    
    customer = relationship("Customer", back_populates="real_estate_projects")
    leads = relationship("Lead", secondary=project_leads, back_populates="real_estate_projects") 