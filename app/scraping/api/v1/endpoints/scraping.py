from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.deps import get_current_active_user
from app.models.models import User, ScrapingConfig, ScrapedLead as ScrapedLeadModel
from app.scraping.services.scraper import ScraperService
from app.scraping.schemas.scraping import (
    ScrapingConfigCreate,
    ScrapingConfigUpdate,
    ScrapingConfigResponse,
    ScrapingResult,
    ScrapedLead
)
from app.api.deps import get_db

router = APIRouter()

@router.get("/config", response_model=ScrapingConfigResponse)
def get_scraping_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get scraping configuration for the current customer."""
    config = db.query(ScrapingConfig).filter(
        ScrapingConfig.customer_id == current_user.customer_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Scraping configuration not found")
    
    return config

@router.post("/config", response_model=ScrapingConfigResponse)
def create_scraping_config(
    config: ScrapingConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create scraping configuration for the current customer."""
    existing_config = db.query(ScrapingConfig).filter(
        ScrapingConfig.customer_id == current_user.customer_id
    ).first()
    
    if existing_config:
        raise HTTPException(status_code=400, detail="Scraping configuration already exists")
    
    db_config = ScrapingConfig(
        customer_id=current_user.customer_id,
        **config.dict()
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config

@router.put("/config", response_model=ScrapingConfigResponse)
def update_scraping_config(
    config: ScrapingConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update scraping configuration for the current customer."""
    db_config = db.query(ScrapingConfig).filter(
        ScrapingConfig.customer_id == current_user.customer_id
    ).first()
    
    if not db_config:
        raise HTTPException(status_code=404, detail="Scraping configuration not found")
    
    for field, value in config.dict(exclude_unset=True).items():
        setattr(db_config, field, value)
    
    db.commit()
    db.refresh(db_config)
    
    return db_config

@router.post("/start", response_model=Dict[str, Any])
def start_scraping(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start scraping process for the current customer."""
    scraper_service = ScraperService(db)
    
    try:
        # Start scraping in background
        background_tasks.add_task(
            scraper_service.scrape_all_sources,
            current_user.customer_id
        )
        
        return {"message": "Scraping started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule", response_model=Dict[str, Any])
def schedule_scraping(
    interval_hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Schedule automatic scraping for the current customer."""
    scraper_service = ScraperService(db)
    
    try:
        scraper_service.schedule_scraping(current_user.customer_id, interval_hours)
        return {"message": f"Scraping scheduled every {interval_hours} hours"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop", response_model=Dict[str, Any])
def stop_scraping(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Stop automatic scraping for the current customer."""
    scraper_service = ScraperService(db)
    
    try:
        scraper_service.stop_scraping(current_user.customer_id)
        return {"message": "Scraping stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results", response_model=Dict[str, List[ScrapingResult]])
def get_scraping_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get latest scraping results for the current customer."""
    scraper_service = ScraperService(db)
    
    try:
        results = scraper_service.scrape_all_sources(current_user.customer_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-options", response_model=Dict[str, Any])
def get_available_options():
    """Get available sources, property types, and locations for scraping config UI."""
    return {
        "sources": ["magicbricks", "housing", "proptiger", "commonfloor"],
        "property_types": ["apartment", "villa", "plot"],
        "locations": ["Mumbai", "Bangalore", "Delhi"]
    }

@router.get("/logs", response_model=List[Dict[str, Any]])
def get_scraping_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get scraping history/logs for the current customer."""
    # Dummy logs for now
    return [
        {"timestamp": "2024-06-01T10:00:00Z", "status": "success", "source": "magicbricks", "properties": 120},
        {"timestamp": "2024-06-01T09:00:00Z", "status": "error", "source": "housing", "error": "Timeout"}
    ]

@router.get("/scraped-leads", response_model=List[ScrapedLead])
def list_scraped_leads(
    lead_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    q = db.query(ScrapedLeadModel).filter(ScrapedLeadModel.customer_id == current_user.customer_id)
    if lead_type:
        q = q.filter(ScrapedLeadModel.lead_type == lead_type)
    return q.order_by(ScrapedLeadModel.created_at.desc()).all()

@router.get("/scraped-leads/{id}", response_model=ScrapedLead)
def get_scraped_lead(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    lead = db.query(ScrapedLeadModel).filter(ScrapedLeadModel.id == id, ScrapedLeadModel.customer_id == current_user.customer_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Scraped lead not found")
    return lead

@router.post("/scraped-leads", response_model=ScrapedLead)
def create_scraped_lead(scraped_lead: ScrapedLead, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_lead = ScrapedLeadModel(**scraped_lead.dict(), customer_id=current_user.customer_id)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.patch("/scraped-leads/{id}", response_model=ScrapedLead)
def update_scraped_lead(id: str, scraped_lead: ScrapedLead, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_lead = db.query(ScrapedLeadModel).filter(ScrapedLeadModel.id == id, ScrapedLeadModel.customer_id == current_user.customer_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Scraped lead not found")
    for field, value in scraped_lead.dict(exclude_unset=True).items():
        setattr(db_lead, field, value)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.delete("/scraped-leads/{id}")
def delete_scraped_lead(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_lead = db.query(ScrapedLeadModel).filter(ScrapedLeadModel.id == id, ScrapedLeadModel.customer_id == current_user.customer_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Scraped lead not found")
    db.delete(db_lead)
    db.commit()
    return {"message": "Scraped lead deleted"} 