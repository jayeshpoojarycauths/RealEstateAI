from datetime import datetime
from typing import Any, List, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Path, status
from sqlalchemy.orm import Session

from app.shared.core.security.auth import get_current_user
from app.shared.core.security import (
    manager_required,
    agent_required,
    viewer_required,
    admin_required,
    get_current_customer
)
from app.shared.core.exceptions import (
    NotFoundException,
    ValidationException,
    AuthorizationException
)
from app.shared.models.user import User
from app.shared.models.project import Project
from app.shared.models.customer import Customer
from app.shared.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectFilter,
    ProjectStats,
    ProjectAnalytics,
    ProjectLeadCreate,
    ProjectLeadResponse,
    ProjectListResponse,
    ProjectList,
    ProjectFeature,
    ProjectFeatureCreate,
    ProjectImage,
    ProjectImageCreate,
    ProjectAmenity,
    ProjectAmenityCreate,
    ProjectLead
)
from app.project.schemas.project import (
    RealEstateProjectCreate,
    RealEstateProjectUpdate,
    RealEstateProjectList,
    RealEstateProject
)
from app.project.services.project import ProjectService
from app.shared.core.scraper import MagicBricksScraper, NinetyNineAcresScraper 
from app.shared.core.exceptions import ValidationError, NotFoundError
from app.shared.db.session import get_db
from app.shared.core.pagination import PaginationParams

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
    current_user: User = Depends(get_current_user),
    source: str,
    location: str,
    max_pages: int = 1,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Trigger scraping of properties from specified source."""
    try:
        scraper = None
        if source.lower() == "magicbricks":
            scraper = MagicBricksScraper(db, current_user.customer_id)
        elif source.lower() == "99acres":
            scraper = NinetyNineAcresScraper(db, current_user.customer_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating scraping: {str(e)}"
        )

@router.get("/properties", response_model=List[RealEstateProject])
async def get_properties(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    location: Optional[str] = None,
    min_price: Optional[str] = None,
    max_price: Optional[str] = None,
    property_type: Optional[str] = None
) -> List[RealEstateProject]:
    """Get properties for the current customer with optional filters."""
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

@router.get("/", response_model=ProjectList)
async def list_projects(
    *,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
    filter_params: ProjectFilter = Depends(),
    pagination: PaginationParams = Depends()
) -> ProjectList:
    """List all projects for the current customer with filtering."""
    project_service = ProjectService(db)
    projects, total = await project_service.list_projects(
        customer_id=current_customer.id,
        filter_params=filter_params,
        pagination=pagination
    )
    return ProjectList(items=projects, total=total)

@router.post("/", response_model=ProjectResponse)
async def create_project(
    *,
    db: Session = Depends(get_db),
    project_in: ProjectCreate,
    current_customer: Customer = Depends(get_current_customer),
    current_user: User = Depends(get_current_user)
) -> ProjectResponse:
    """Create a new project."""
    project_service = ProjectService(db)
    try:
        project = await project_service.create_project(
            project_in=project_in,
            customer_id=current_customer.id
        )
        return project
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    *,
    db: Session = Depends(get_db),
    project_id: UUID = Path(...),
    current_customer: Customer = Depends(get_current_customer)
) -> ProjectResponse:
    """Get a specific project."""
    project_service = ProjectService(db)
    try:
        project = await project_service.get_project(
            project_id=project_id,
            customer_id=current_customer.id
        )
        return project
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    *,
    db: Session = Depends(get_db),
    project_id: UUID = Path(...),
    project_in: ProjectUpdate,
    current_customer: Customer = Depends(get_current_customer)
) -> ProjectResponse:
    """Update a project."""
    project_service = ProjectService(db)
    try:
        project = await project_service.update_project(
            project_id=project_id,
            project_in=project_in,
            customer_id=current_customer.id
        )
        return project
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    *,
    db: Session = Depends(get_db),
    project_id: UUID = Path(...),
    current_customer: Customer = Depends(get_current_customer)
) -> None:
    """Delete a project."""
    project_service = ProjectService(db)
    try:
        await project_service.delete_project(
            project_id=project_id,
            customer_id=current_customer.id
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{project_id}/features", response_model=ProjectFeature)
async def add_feature(
    *,
    db: Session = Depends(get_db),
    project_id: UUID = Path(...),
    feature_in: ProjectFeatureCreate,
    current_customer: dict = Depends(get_current_customer),
    current_user: dict = Depends(get_current_user)
):
    """Add a feature to a project."""
    project_service = ProjectService(db)
    try:
        feature = await project_service.add_feature(
            project_id=project_id,
            feature_in=feature_in,
            customer_id=current_customer["id"],
            user_id=current_user["id"]
        )
        return feature
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{project_id}/images", response_model=ProjectImage)
async def add_image(
    *,
    db: Session = Depends(get_db),
    project_id: UUID = Path(...),
    image_in: ProjectImageCreate,
    current_customer: dict = Depends(get_current_customer),
    current_user: dict = Depends(get_current_user)
):
    """Add an image to a project."""
    project_service = ProjectService(db)
    try:
        image = await project_service.add_image(
            project_id=project_id,
            image_in=image_in,
            customer_id=current_customer["id"],
            user_id=current_user["id"]
        )
        return image
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{project_id}/amenities", response_model=ProjectAmenity)
async def add_amenity(
    *,
    db: Session = Depends(get_db),
    project_id: UUID = Path(...),
    amenity_in: ProjectAmenityCreate,
    current_customer: dict = Depends(get_current_customer),
    current_user: dict = Depends(get_current_user)
):
    """Add an amenity to a project."""
    project_service = ProjectService(db)
    try:
        amenity = await project_service.add_amenity(
            project_id=project_id,
            amenity_in=amenity_in,
            customer_id=current_customer["id"],
            user_id=current_user["id"]
        )
        return amenity
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{project_id}/leads", response_model=ProjectLead)
async def assign_lead(
    *,
    db: Session = Depends(get_db),
    project_id: UUID = Path(...),
    lead_in: ProjectLeadCreate,
    current_customer: dict = Depends(get_current_customer),
    current_user: dict = Depends(get_current_user)
):
    """Assign a lead to a project."""
    project_service = ProjectService(db)
    try:
        lead_assignment = await project_service.assign_lead(
            project_id=project_id,
            lead_in=lead_in,
            customer_id=current_customer["id"]
        )
        return lead_assignment
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats", response_model=ProjectStats)
async def get_project_stats(
    *,
    db: Session = Depends(get_db),
    current_customer: dict = Depends(get_current_customer),
    current_user: dict = Depends(get_current_user)
):
    """Get project statistics."""
    project_service = ProjectService(db)
    stats = await project_service.get_project_stats(
        customer_id=current_customer["id"]
    )
    return stats

@router.get("/analytics", response_model=ProjectAnalytics)
async def get_project_analytics(
    *,
    db: Session = Depends(get_db),
    current_customer: dict = Depends(get_current_customer),
    current_user: dict = Depends(get_current_user)
):
    """Get project analytics."""
    project_service = ProjectService(db)
    analytics = await project_service.get_project_analytics(
        customer_id=current_customer["id"]
    )
    return analytics 