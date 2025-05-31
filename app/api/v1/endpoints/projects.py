from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import User, Customer, Project
from app.schemas.project import ProjectCreate, ProjectUpdate, Project as ProjectSchema

router = APIRouter()

@router.get("/", response_model=List[ProjectSchema])
async def get_projects(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    skip: int = 0,
    limit: int = 100
) -> List[ProjectSchema]:
    """Get list of real estate projects for the current customer."""
    projects = db.query(Project).filter(
        Project.customer_id == current_customer.id
    ).offset(skip).limit(limit).all()
    return projects

@router.post("/", response_model=ProjectSchema)
async def create_project(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    project_in: ProjectCreate
) -> ProjectSchema:
    """Create a new real estate project."""
    project = Project(
        **project_in.dict(),
        customer_id=current_customer.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    project_id: str,
    project_in: ProjectUpdate
) -> ProjectSchema:
    """Update a real estate project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.customer_id == current_customer.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", response_model=ProjectSchema)
async def delete_project(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    project_id: str
) -> ProjectSchema:
    """Delete a real estate project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.customer_id == current_customer.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return project 