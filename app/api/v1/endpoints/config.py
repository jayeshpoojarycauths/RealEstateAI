from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel

from app.core.deps import get_current_active_user
from app.api.deps import get_db, get_current_customer
from app.models.models import User, CommunicationPreferences, ScrapingConfig, Customer, Lead
from app.schemas.communication import CommunicationPreferencesCreate, CommunicationPreferenceUpdate, CommunicationPreference
from app.schemas.config import ConfigUpdate, ConfigResponse

router = APIRouter()

# Communication Configuration Endpoints
@router.get("/", response_model=ConfigResponse)
async def get_config(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get configuration for the current customer."""
    preferences = db.query(CommunicationPreferences).filter(
        CommunicationPreferences.customer_id == current_customer.id
    ).first()
    if not preferences:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return preferences

@router.put("/", response_model=ConfigResponse)
async def update_config(
    *,
    db: Session = Depends(get_db),
    config_in: ConfigUpdate,
    current_user = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
):
    """Update configuration for the current customer."""
    preferences = db.query(CommunicationPreferences).filter(
        CommunicationPreferences.customer_id == current_customer.id
    ).first()
    if not preferences:
        preferences = CommunicationPreferences(customer_id=current_customer.id)
        db.add(preferences)
    
    for field, value in config_in.dict(exclude_unset=True).items():
        setattr(preferences, field, value)
    
    db.commit()
    db.refresh(preferences)
    return preferences

# Scraping Configuration Endpoints
class ScrapingConfigBase(BaseModel):
    enabled_sources: List[str] = ["magicbricks", "99acres", "housing"]
    scraping_delay: int = 2
    max_retries: int = 3
    proxy_enabled: bool = False
    proxy_url: str = None
    user_agent: str = None
    max_pages_per_source: int = 5
    auto_scrape_enabled: bool = False
    auto_scrape_interval: int = 24  # hours
    locations: List[str] = []
    property_types: List[str] = []
    price_range_min: float = None
    price_range_max: float = None

class ScrapingConfigCreate(ScrapingConfigBase):
    customer_id: UUID

class ScrapingConfigUpdate(ScrapingConfigBase):
    pass

class ScrapingConfig(ScrapingConfigBase):
    id: UUID
    customer_id: UUID

    class Config:
        from_attributes = True

@router.get("/scraping", response_model=ScrapingConfig)
async def get_scraping_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get scraping configuration for the current customer
    """
    config = db.query(ScrapingConfig).filter(
        ScrapingConfig.customer_id == current_user.customer_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="Scraping configuration not found"
        )
    
    return config

@router.post("/scraping", response_model=ScrapingConfig)
async def create_scraping_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    config: ScrapingConfigCreate,
) -> Any:
    """
    Create scraping configuration for the current customer
    """
    existing_config = db.query(ScrapingConfig).filter(
        ScrapingConfig.customer_id == current_user.customer_id
    ).first()
    
    if existing_config:
        raise HTTPException(
            status_code=400,
            detail="Scraping configuration already exists"
        )
    
    db_config = ScrapingConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config

@router.put("/scraping", response_model=ScrapingConfig)
async def update_scraping_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    config: ScrapingConfigUpdate,
) -> Any:
    """
    Update scraping configuration for the current customer
    """
    db_config = db.query(ScrapingConfig).filter(
        ScrapingConfig.customer_id == current_user.customer_id
    ).first()
    
    if not db_config:
        raise HTTPException(
            status_code=404,
            detail="Scraping configuration not found"
        )
    
    for field, value in config.dict(exclude_unset=True).items():
        setattr(db_config, field, value)
    
    db.commit()
    db.refresh(db_config)
    
    return db_config 