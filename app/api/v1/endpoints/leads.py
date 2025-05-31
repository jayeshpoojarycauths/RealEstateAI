from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import User, Customer, Lead
from app.schemas.lead import LeadCreate, LeadUpdate, Lead as LeadSchema
from app.lead.services.lead import LeadService
import pandas as pd
from io import BytesIO
from uuid import UUID
from fastapi.responses import FileResponse
import tempfile
from app.schemas.interaction import LeadScore, InteractionLog
from app.services.lead_scoring import LeadScoringService
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[LeadSchema])
async def get_leads(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    skip: int = 0,
    limit: int = 1000,
) -> List[LeadSchema]:
    """Get list of leads for the current customer."""
    print("[DEBUG] get_leads endpoint called")
    print(f"[DEBUG] current_user: {getattr(current_user, 'id', None)}")
    print(f"[DEBUG] current_customer: {getattr(current_customer, 'id', None)}")
    leads = db.query(Lead).filter(
        Lead.customer_id == current_customer.id
    ).offset(skip).limit(limit).all()
    print(f"[DEBUG] leads returned: {len(leads)}")
    return leads

@router.post("/", response_model=LeadSchema)
async def create_lead(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    lead_in: LeadCreate
) -> LeadSchema:
    """Create a new lead."""
    # Duplicate email check
    if lead_in.email:
        existing = db.query(Lead).filter(Lead.email == lead_in.email, Lead.customer_id == current_customer.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="A lead with this email already exists.")
    lead_data = lead_in.dict()
    first_name = lead_data.pop("first_name", "")
    last_name = lead_data.pop("last_name", "")
    lead_data.pop("name", None)  # Remove name if present
    lead_data.pop("created_by", None)  # Remove created_by if present
    name = f"{first_name} {last_name}".strip()
    now = datetime.utcnow()
    lead = Lead(
        **lead_data,
        name=name,
        customer_id=current_customer.id,
        created_by=current_user.id,
        updated_by=current_user.id,
        updated_at=now
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.put("/{lead_id}", response_model=LeadSchema)
async def update_lead(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    lead_id: str,
    lead_in: LeadUpdate
) -> LeadSchema:
    """Update a lead."""
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.customer_id == current_customer.id
    ).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead_in.dict(exclude_unset=True)
    first_name = update_data.pop("first_name", "")
    last_name = update_data.pop("last_name", "")
    update_data.pop("name", None)  # Remove name if present
    update_data.pop("updated_by", None)  # Remove updated_by if present
    if first_name or last_name:
        update_data["name"] = f"{first_name} {last_name}".strip()
    for field, value in update_data.items():
        setattr(lead, field, value)
    lead.updated_by = current_user.id
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.delete("/{lead_id}", response_model=LeadSchema)
async def delete_lead(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    lead_id: str
) -> LeadSchema:
    """Delete a lead."""
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.customer_id == current_customer.id
    ).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    return lead

@router.post("/upload", summary="Upload leads via CSV/Excel", tags=["leads"])
async def upload_leads(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """
    Upload leads in bulk via CSV or Excel file. Matches by email: updates if found, creates if not.
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are supported.")

    contents = await file.read()
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents))
        else:
            df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    required_columns = {"email", "name"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Missing required columns: {required_columns - set(df.columns)}")

    lead_service = LeadService(db)
    result = lead_service.bulk_upload_leads(df, current_customer.id, db)
    return result

@router.post("/new/", response_model=LeadSchema)
async def create_lead_new(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    lead_in: LeadCreate
) -> LeadSchema:
    """Create a new lead (new endpoint)."""
    # Duplicate email check
    if lead_in.email:
        existing = db.query(Lead).filter(Lead.email == lead_in.email, Lead.customer_id == current_customer.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="A lead with this email already exists.")
    lead_data = lead_in.dict()
    first_name = lead_data.pop("first_name", "")
    last_name = lead_data.pop("last_name", "")
    lead_data.pop("name", None)  # Remove name if present
    lead_data.pop("created_by", None)  # Remove created_by if present
    lead_data.pop("updated_by", None)  # Remove updated_by if present
    name = f"{first_name} {last_name}".strip()
    now = datetime.utcnow()
    lead = Lead(
        **lead_data,
        name=name,
        customer_id=current_customer.id,
        created_by=current_user.id,
        updated_by=current_user.id,
        updated_at=now
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.put("/edit/{lead_id}", response_model=LeadSchema)
async def update_lead_new(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer),
    lead_id: str,
    lead_in: LeadUpdate
) -> LeadSchema:
    """Update a lead (new endpoint)."""
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.customer_id == current_customer.id
    ).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.get("/{lead_id}/score", response_model=LeadScore)
def get_lead_score(
    lead_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Get lead score."""
    scoring_service = LeadScoringService(db)
    try:
        lead_score = scoring_service.update_lead_score(lead_id)
        return lead_score
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{lead_id}/interactions", response_model=List[InteractionLog])
def get_lead_interactions(
    lead_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Get lead interaction history."""
    scoring_service = LeadScoringService(db)
    return scoring_service.get_lead_interaction_history(lead_id)

@router.get("/template")
async def get_upload_template(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get a template file for lead uploads.
    """
    lead_service = LeadService(db)
    template_df = lead_service.get_upload_template()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        template_df.to_excel(temp_file.name, index=False)
        return FileResponse(
            temp_file.name,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename='lead_upload_template.xlsx',
            background=None
        ) 