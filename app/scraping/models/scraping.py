from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Text, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.shared.db.base_class import BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid

class ScrapingSource(str, enum.Enum):
    """Supported scraping sources."""
    MAGICBRICKS = "magicbricks"
    NINETY_NINE_ACRES = "99acres"
    HOUSING = "housing"
    PROPTIGER = "proptiger"
    COMMONFLOOR = "commonfloor"
    FACEBOOK_MARKETPLACE = "facebook_marketplace"

class ScrapingStatus(str, enum.Enum):
    """Status of scraping jobs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ScrapingConfig(BaseModel):
    """Model for scraping configuration."""
    __tablename__ = "scraping_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    enabled_sources = Column(JSON, default=list)
    locations = Column(JSON, default=list)
    property_types = Column(JSON, default=list)
    price_range_min = Column(Float)
    price_range_max = Column(Float)
    max_pages_per_source = Column(Integer, default=5)
    scraping_delay = Column(Integer, default=2)  # seconds
    max_retries = Column(Integer, default=3)
    proxy_enabled = Column(Boolean, default=False)
    proxy_url = Column(String(255))
    user_agent = Column(String(255))
    auto_scrape_enabled = Column(Boolean, default=False)
    auto_scrape_interval = Column(Integer, default=24)  # hours
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="scraping_config")
    jobs = relationship("ScrapingJob", back_populates="config")
    
    def __repr__(self):
        return f"<ScrapingConfig {self.customer_id}>"

class ScrapingJob(BaseModel):
    """Model for tracking scraping jobs."""
    __tablename__ = "scraping_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(UUID(as_uuid=True), ForeignKey("scraping_configs.id", ondelete="CASCADE"), nullable=False)
    source = Column(Enum(ScrapingSource), nullable=False)
    status = Column(Enum(ScrapingStatus), nullable=False, default=ScrapingStatus.PENDING)
    location = Column(String(100))
    property_type = Column(String(50))
    items_scraped = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    config = relationship("ScrapingConfig", back_populates="jobs")
    results = relationship("ScrapingResult", back_populates="job")
    
    def __repr__(self):
        return f"<ScrapingJob {self.id} - {self.source}>"

class ScrapingResult(BaseModel):
    """Model for storing scraping results."""
    __tablename__ = "scraping_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("scraping_jobs.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float)
    location = Column(String(100))
    property_type = Column(String(50))
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    area = Column(Float)
    images = Column(JSON)
    source_url = Column(String(255))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    job = relationship("ScrapingJob", back_populates="results")
    
    def __repr__(self):
        return f"<ScrapingResult {self.id} - {self.title}>" 