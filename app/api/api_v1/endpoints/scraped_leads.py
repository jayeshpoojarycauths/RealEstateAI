from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
from app.models.models import User
from app.scraping.schemas.scraping import ScrapedLead
from app.services import scraped_lead as scraped_lead_service
from app.services.scraper import ScraperService
from fastapi import BackgroundTasks
import asyncio

router = APIRouter()

@router.get("/scraped-leads", response_model=List[ScrapedLead])
def list_scraped_leads(
    lead_type: Optional[str] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    return scraped_lead_service.get_scraped_leads(db, current_user.customer_id, lead_type)

@router.get("/scraped-leads/{id}", response_model=ScrapedLead)
def get_scraped_lead(id: str, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_active_user)):
    lead = scraped_lead_service.get_scraped_lead(db, current_user.customer_id, id)
    if not lead:
        raise HTTPException(status_code=404, detail="Scraped lead not found")
    return lead

@router.post("/scraped-leads", response_model=ScrapedLead)
def create_scraped_lead(scraped_lead: ScrapedLead, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_active_user)):
    return scraped_lead_service.create_scraped_lead(db, current_user.customer_id, scraped_lead.lead_type, scraped_lead.data, scraped_lead.source)

@router.patch("/scraped-leads/{id}", response_model=ScrapedLead)
def update_scraped_lead(id: str, scraped_lead: ScrapedLead, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_active_user)):
    updated = scraped_lead_service.update_scraped_lead(db, current_user.customer_id, id, scraped_lead.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Scraped lead not found")
    return updated

@router.delete("/scraped-leads/{id}")
def delete_scraped_lead(id: str, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_active_user)):
    deleted = scraped_lead_service.delete_scraped_lead(db, current_user.customer_id, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scraped lead not found")
    return {"message": "Scraped lead deleted"}

@router.post("/scraped-leads/scrape-users", response_model=List[ScrapedLead])
def scrape_users(
    location: str = "",
    max_pages: int = 5,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    service = ScraperService(db)
    # Run synchronously for now; can be moved to background if needed
    return asyncio.run(service.scrape_users(current_user.customer_id, location, max_pages))

@router.post("/scraped-leads/scrape-locations", response_model=List[ScrapedLead])
def scrape_locations(
    max_pages: int = 5,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    service = ScraperService(db)
    return asyncio.run(service.scrape_locations(current_user.customer_id, max_pages)) 