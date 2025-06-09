from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.scraping.models.scraping import ScrapingSource, ScrapingStatus
from app.scraping.schemas.scraping import (ScrapingConfig,
                                           ScrapingConfigCreate,
                                           ScrapingConfigList,
                                           ScrapingConfigUpdate, ScrapingJob,
                                           ScrapingJobList,
                                           ScrapingResultList,
                                           ScrapingStats)
from app.shared.core.exceptions import NotFoundError, ValidationError
from app.shared.core.security.auth import get_current_user
from app.shared.db.session import get_db

router = APIRouter()

@router.post("/configs", response_model=ScrapingConfig)
async def create_scraping_config(
    config: ScrapingConfigCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new scraping configuration."""
    from app.scraping.services.scraper import ScraperService
    service = ScraperService(db)
    try:
        return await service.create_config(config, current_user.id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/configs", response_model=ScrapingConfigList)
async def list_scraping_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all scraping configurations for the current user."""
    from app.scraping.services.scraper import ScraperService
    service = ScraperService(db)
    return await service.list_configs(current_user.id, skip, limit)

@router.get("/configs/{config_id}", response_model=ScrapingConfig)
async def get_scraping_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific scraping configuration."""
    from app.scraping.services.scraper import ScraperService
    service = ScraperService(db)
    try:
        return await service.get_config(config_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/configs/{config_id}", response_model=ScrapingConfig)
async def update_scraping_config(
    config_id: str,
    config: ScrapingConfigUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a scraping configuration."""
    from app.scraping.services.scraper import ScraperService
    service = ScraperService(db)
    try:
        return await service.update_config(config_id, config, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/configs/{config_id}")
async def delete_scraping_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a scraping configuration."""
    from app.scraping.services.scraper import ScraperService
    service = ScraperService(db)
    try:
        await service.delete_config(config_id, current_user.id)
        return {"message": "Configuration deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/jobs", response_model=ScrapingJob)
async def create_scraping_job(
    config_id: str,
    source: ScrapingSource,
    location: str,
    property_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create and run a new scraping job."""
    from app.scraping.services.scraper import ScraperService
    service = ScraperService(db)
    try:
        return await service.run_scraping_job(config_id, source, location, property_type)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/jobs", response_model=ScrapingJobList)
async def list_scraping_jobs(
    config_id: Optional[str] = None,
    source: Optional[ScrapingSource] = None,
    status: Optional[ScrapingStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List scraping jobs with optional filters."""
    from app.scraping.services.scraper import ScraperService
    service = ScraperService(db)
    return service.list_jobs(
        config_id=config_id,
        source=source,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

@router.get("/jobs/{job_id}", response_model=ScrapingJob)
async def get_scraping_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific scraping job."""
    from app.scraping.services.scraper import ScraperService
    service = ScraperService(db)
    try:
        return service.get_job_status(job_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/jobs/{job_id}/results", response_model=ScrapingResultList)
async def get_job_results(
    job_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get results for a specific scraping job."""
    from app.scraping.services.scraper import ScraperService
    service = ScraperService(db)
    try:
        results = service.get_job_results(job_id, skip, limit)
        return {
            "items": results,
            "total": len(results),
            "skip": skip,
            "limit": limit
        }
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/configs/{config_id}/stats", response_model=ScrapingStats)
async def get_scraping_stats(
    config_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get scraping statistics for a configuration."""
    from app.scraping.services.scraper import ScraperService
    service = ScraperService(db)
    try:
        return service.get_scraping_stats(config_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/scheduled/run")
async def run_scheduled_jobs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Run all scheduled scraping jobs."""
    from app.scraping.services.scraper import ScraperService
    service = ScraperService(db)
    await service.run_scheduled_jobs()
    return {"message": "Scheduled jobs started successfully"} 