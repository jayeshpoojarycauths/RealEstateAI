from typing import Any, List

from fastapi import (APIRouter, Depends, File, HTTPException, UploadFile, status)
from sqlalchemy.orm import Session

from app.lead.schemas.lead import (LeadActivityCreate, LeadCreate, LeadResponse, LeadUpdate,
                                   LeadUploadResponse)
from app.lead.services.lead import LeadService
from app.shared.api import deps
from app.shared.core.security.dependencies import require_role
from app.shared.core.security.roles import Role
from app.shared.models.user import User

router = APIRouter()

@require_role([Role.ADMIN, Role.AGENT])
@router.post("/upload", response_model=LeadUploadResponse)
async def upload_leads(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Upload leads from a file."""
    lead_service = LeadService(db)
    return await lead_service.upload_leads(db, file, current_user)

@require_role([Role.ADMIN, Role.AGENT])
@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get a list of leads."""
    lead_service = LeadService(db)
    return await lead_service.get_leads(db, skip, limit, current_user)

@require_role([Role.ADMIN, Role.AGENT])
@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create a new lead."""
    lead_service = LeadService(db)
    return await lead_service.create_lead(db, lead_in, current_user)

@require_role([Role.ADMIN, Role.AGENT])
@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get a lead by ID."""
    lead_service = LeadService(db)
    lead = await lead_service.get_lead(db, lead_id, current_user)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    return lead

@require_role([Role.ADMIN, Role.AGENT])
@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_in: LeadUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Update a lead."""
    lead_service = LeadService(db)
    lead = await lead_service.update_lead(db, lead_id, lead_in, current_user)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    return lead

@require_role([Role.ADMIN])
@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Delete a lead."""
    lead_service = LeadService(db)
    if not await lead_service.delete_lead(db, lead_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

@require_role([Role.ADMIN, Role.AGENT])
@router.post("/{lead_id}/activities", response_model=Any)
async def create_lead_activity(
    lead_id: str,
    activity_in: LeadActivityCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create a new activity for a lead."""
    lead_service = LeadService(db)
    return await lead_service.create_activity(db, lead_id, activity_in, current_user)

@require_role([Role.ADMIN, Role.AGENT])
@router.get("/{lead_id}/activities", response_model=List[Any])
async def list_lead_activities(
    lead_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """List all activities for a lead."""
    lead_service = LeadService(db)
    return await lead_service.get_activities(db, lead_id, current_user)

@require_role([Role.ADMIN, Role.AGENT])
@router.post("/{lead_id}/assign", response_model=Any)
async def assign_lead(
    lead_id: str,
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Assign a lead to a user."""
    lead_service = LeadService(db)
    return await lead_service.assign_lead(db, lead_id, user_id, current_user)

@require_role([Role.ADMIN, Role.AGENT])
@router.get("/stats", response_model=Any)
async def get_lead_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get lead statistics."""
    lead_service = LeadService(db)
    return await lead_service.get_stats(db, current_user) 