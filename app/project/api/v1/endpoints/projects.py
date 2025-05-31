from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.core.deps import get_current_active_user
from app.shared.db.session import get_db
from app.models.models import User, RealEstateProject, Customer, Project, ProjectLead
from app.services.scraper import MagicBricksScraper, NinetyNineAcresScraper
from app.api.deps import get_current_user, get_current_customer
from app.project.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectFilter,
    ProjectStats, ProjectAnalytics, ProjectLeadCreate, ProjectLeadResponse,
    ProjectListResponse
)
from app.project.services.project import ProjectService
from app.core.pagination import PaginationParams, get_pagination_params
from app.core.security import admin_required, manager_required, agent_required, viewer_required
from app.schemas.property import (
    RealEstateProjectCreate,
    RealEstateProjectUpdate,
    RealEstateProjectList,
    RealEstateProject
)

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"}
    }
)

@router.post("/scrape/{source}")
async def scrape_properties(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    source: str,
    location: str,
    max_pages: int = 1,
    background_tasks: BackgroundTasks
) -> Any:
    """
    Trigger scraping of properties from specified source
    """
    try:
        scraper = None
        if source.lower() == "magicbricks":
            scraper = MagicBricksScraper(db, current_user.customer_id)
        elif source.lower() == "99acres":
            scraper = NinetyNineAcresScraper(db, current_user.customer_id)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported source: {source}"
            )
        
        # Run scraping in background
        background_tasks.add_task(
            scraper.scrape_properties,
            location=location,
            max_pages=max_pages
        )
        
        return {
            "message": "Scraping initiated",
            "source": source,
            "location": location,
            "max_pages": max_pages
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initiating scraping: {str(e)}"
        )

@router.get("/properties", response_model=List[RealEstateProject])
async def get_properties(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    location: str = None,
    min_price: str = None,
    max_price: str = None,
    property_type: str = None
) -> List[RealEstateProject]:
    """
    Get properties for the current customer with optional filters
    """
    query = db.query(RealEstateProject).filter(
        RealEstateProject.customer_id == current_user.customer_id
    )
    
    if location:
        query = query.filter(RealEstateProject.location.ilike(f"%{location}%"))
    if min_price:
        query = query.filter(RealEstateProject.price >= min_price)
    if max_price:
        query = query.filter(RealEstateProject.price <= max_price)
    if property_type:
        query = query.filter(RealEstateProject.type.ilike(f"%{property_type}%"))
    
    properties = query.offset(skip).limit(limit).all()
    return properties

@router.get("/", response_model=RealEstateProjectList)
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_customer: Customer = Depends(get_current_customer)
) -> RealEstateProjectList:
    """Get list of real estate projects."""
    project_service = ProjectService(db)
    return await project_service.get_projects(
        customer_id=current_customer.id,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=RealEstateProject)
async def create_project(
    project: RealEstateProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_customer: Customer = Depends(get_current_customer)
) -> RealEstateProject:
    """Create a new real estate project."""
    project_service = ProjectService(db)
    return await project_service.create_project(
        customer_id=current_customer.id,
        project=project
    )

@router.get("/{project_id}", response_model=RealEstateProject)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_customer: Customer = Depends(get_current_customer)
) -> RealEstateProject:
    """Get a specific real estate project."""
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id)
    if not project or project.customer_id != current_customer.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=RealEstateProject)
async def update_project(
    project_id: int,
    project: RealEstateProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_customer: Customer = Depends(get_current_customer)
) -> RealEstateProject:
    """Update a real estate project."""
    project_service = ProjectService(db)
    updated_project = await project_service.update_project(
        project_id=project_id,
        customer_id=current_customer.id,
        project=project
    )
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_customer: Customer = Depends(get_current_customer)
) -> Dict[str, Any]:
    """Delete a real estate project."""
    project_service = ProjectService(db)
    success = await project_service.delete_project(
        project_id=project_id,
        customer_id=current_customer.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "success", "message": "Project deleted successfully"}

@router.get("/{project_id}/stats", response_model=ProjectStats)
async def get_project_stats(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(viewer_required())
):
    """
    Get project statistics.
    
    - **project_id**: ID of the project
    - **current_user**: Current authenticated user
    
    Returns project statistics including lead counts and conversion rates.
    """
    project_service = ProjectService(db)
    stats = await project_service.get_project_stats(project_id, current_user.customer_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Project not found")
    return stats

@router.get("/{project_id}/analytics", response_model=ProjectAnalytics)
async def get_project_analytics(
    project_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(viewer_required())
):
    """
    Get project analytics with date range filtering.
    
    - **project_id**: ID of the project
    - **start_date**: Start date for analytics (YYYY-MM-DD)
    - **end_date**: End date for analytics (YYYY-MM-DD)
    - **current_user**: Current authenticated user
    
    Returns project analytics including lead trends and status distribution.
    """
    project_service = ProjectService(db)
    analytics = await project_service.get_project_analytics(
        project_id,
        current_user.customer_id,
        start_date,
        end_date
    )
    if not analytics:
        raise HTTPException(status_code=404, detail="Project not found")
    return analytics

@router.post("/{project_id}/leads/{lead_id}", status_code=status.HTTP_201_CREATED)
async def assign_lead_to_project(
    project_id: int,
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(agent_required())
):
    """
    Assign a lead to a project.
    
    - **project_id**: ID of the project
    - **lead_id**: ID of the lead to assign
    - **current_user**: Current authenticated user (must be agent, manager, or admin)
    
    Returns success message.
    """
    project_service = ProjectService(db)
    success = await project_service.assign_lead(
        project_id, lead_id, current_user.customer_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Project or lead not found")
    return {"message": "Lead assigned successfully"}

@router.delete("/{project_id}/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_lead_from_project(
    project_id: int,
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(agent_required())
):
    """
    Remove a lead from a project.
    
    - **project_id**: ID of the project
    - **lead_id**: ID of the lead to remove
    - **current_user**: Current authenticated user (must be agent, manager, or admin)
    
    Returns no content on success.
    """
    project_service = ProjectService(db)
    success = await project_service.remove_lead(
        project_id, lead_id, current_user.customer_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Project or lead not found") 