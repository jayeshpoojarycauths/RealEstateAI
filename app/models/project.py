import uuid
from datetime import datetime

from sqlalchemy import (JSON, Boolean, Column, DateTime, Enum, Float,
                        ForeignKey, Integer, String)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.project.schemas import PropertyStatus, PropertyType
from app.shared.db.base_class import Base
from datetime import datetime
from datetime import datetime


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    property_type = Column(Enum(PropertyType), nullable=False)
    status = Column(Enum(PropertyStatus), nullable=False, default=PropertyStatus.AVAILABLE)
    location = Column(String(200), nullable=False)
    total_units = Column(Integer)
    price_range = Column(String(100))
    amenities = Column(JSON)
    completion_date = Column(DateTime)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="projects")

    # Location fields
    address = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    features = relationship("PropertyFeature", back_populates="project", cascade="all, delete-orphan")
    images = relationship("PropertyImage", back_populates="project", cascade="all, delete-orphan")
    amenities = relationship("PropertyAmenity", back_populates="project", cascade="all, delete-orphan")

class PropertyFeature(Base):
    __tablename__ = "property_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    value = Column(String(500), nullable=False)
    
    project = relationship("Project", back_populates="features")

class PropertyImage(Base):
    __tablename__ = "property_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    url = Column(String(500), nullable=False)
    caption = Column(String(200), nullable=True)
    is_primary = Column(Boolean, default=False)
    
    project = relationship("Project", back_populates="images")

class PropertyAmenity(Base):
    __tablename__ = "property_amenities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(100), nullable=False)
    
    project = relationship("Project", back_populates="amenities") 