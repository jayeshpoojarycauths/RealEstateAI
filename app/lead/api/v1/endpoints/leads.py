from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO, BytesIO
from uuid import UUID
import tempfile
import os
from fastapi.responses import FileResponse

from app.api import deps
from app.models.models import User, Lead, Customer
from app.lead.schemas.lead import LeadCreate, LeadUploadResponse, LeadUpdate, LeadBulkCreate, LeadResponse, LeadFilter, LeadListResponse, LeadStats, LeadActivityCreate, LeadActivityResponse
from app.lead.schemas.interaction import LeadScore, InteractionLog, CallInteraction, MessageInteraction
from app.lead.services.lead_scoring import LeadScoringService
from app.lead.services.lead import LeadService
from app.core.pagination import PaginationParams, get_pagination_params
from app.core.security import require_role, UserRole
from app.shared.db.session import get_db
from app.core.deps import get_current_active_user, get_current_customer
from app.shared.core.exceptions import ValidationError, NotFoundError

router = APIRouter()

@router.post("/upload", response_model=LeadUploadResponse)
@require_role([UserRole.ADMIN, UserRole.MANAGER])
async def upload_leads(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Upload leads from CSV or Excel file.
    Required columns: name, email, phone, source
    Optional columns: notes, status
    """
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be CSV or Excel"
        )

    try:
        # Read file content
        content = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(content))
        else:
            df = pd.read_excel(BytesIO(content))

        # Validate required columns
        required_columns = ['name', 'email', 'phone', 'source']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        # Process leads
        success_count = 0
        error_count = 0
        errors = []

        for _, row in df.iterrows():
            try:
                lead_data = LeadCreate(
                    name=row['name'],
                    email=row['email'],
                    phone=row['phone'],
                    source=row['source'],
                    notes=row.get('notes', ''),
                    status=row.get('status', 'new'),
                    customer_id=current_user.customer_id
                )
                
                lead = Lead(**lead_data.dict())
                db.add(lead)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Row {_ + 2}: {str(e)}")

        db.commit()

        return LeadUploadResponse(
            success_count=success_count,
            error_count=error_count,
            errors=errors
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """Get all leads for the current customer."""
    leads = db.query(Lead).filter(
        Lead.customer_id == current_customer.id
    ).offset(skip).limit(limit).all()
    return leads

@router.post("/", response_model=LeadResponse)
async def create_lead(
    *,
    db: Session = Depends(get_db),
    lead_in: LeadCreate,
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> Any:
    """Create a new lead."""
    lead_service = LeadService(db)
    try:
        lead = await lead_service.create_lead(
            lead_data=lead_in,
            customer_id=str(current_customer.id),
            user_id=str(current_user.id)
        )
        return lead
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    *,
    db: Session = Depends(get_db),
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> Any:
    """Get a lead by ID."""
    lead_service = LeadService(db)
    try:
        lead = await lead_service.get_lead(
            lead_id=lead_id,
            customer_id=str(current_customer.id)
        )
        return lead
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    *,
    db: Session = Depends(get_db),
    lead_id: int,
    lead_in: LeadUpdate,
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> Any:
    """Update a lead."""
    lead_service = LeadService(db)
    try:
        lead = await lead_service.update_lead(
            lead_id=lead_id,
            lead_data=lead_in,
            customer_id=str(current_customer.id),
            user_id=str(current_user.id)
        )
        return lead
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{lead_id}", response_model=dict)
async def delete_lead(
    *,
    db: Session = Depends(get_db),
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> Any:
    """Delete a lead."""
    lead_service = LeadService(db)
    try:
        await lead_service.delete_lead(
            lead_id=lead_id,
            customer_id=str(current_customer.id),
            user_id=str(current_user.id)
        )
        return {"message": "Lead deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

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

@router.post("/{lead_id}/interactions", response_model=InteractionLog)
def create_interaction(
    lead_id: UUID,
    interaction_type: str,
    status: str,
    user_input: Optional[dict] = None,
    error_message: Optional[str] = None,
    response_time: Optional[float] = None,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Log a new interaction."""
    scoring_service = LeadScoringService(db)
    try:
        interaction = scoring_service.log_interaction(
            lead_id=lead_id,
            customer_id=current_user.customer_id,
            interaction_type=interaction_type,
            status=status,
            user_input=user_input,
            error_message=error_message,
            response_time=response_time
        )
        # Update lead score after new interaction
        scoring_service.update_lead_score(lead_id)
        return interaction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{lead_id}/interactions/call", response_model=CallInteraction)
def log_call_interaction(
    lead_id: UUID,
    call_sid: str,
    recording_url: Optional[str] = None,
    transcript: Optional[str] = None,
    keypad_inputs: Optional[dict] = None,
    menu_selections: Optional[dict] = None,
    call_quality_metrics: Optional[dict] = None,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Log call-specific interaction details."""
    scoring_service = LeadScoringService(db)
    try:
        # First create the base interaction
        interaction = scoring_service.log_interaction(
            lead_id=lead_id,
            customer_id=current_user.customer_id,
            interaction_type="call",
            status="success"
        )
        # Then log call-specific details
        call_interaction = scoring_service.log_call_interaction(
            interaction_id=interaction.id,
            call_sid=call_sid,
            recording_url=recording_url,
            transcript=transcript,
            keypad_inputs=keypad_inputs,
            menu_selections=menu_selections,
            call_quality_metrics=call_quality_metrics
        )
        # Update lead score
        scoring_service.update_lead_score(lead_id)
        return call_interaction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{lead_id}/interactions/message", response_model=MessageInteraction)
def log_message_interaction(
    lead_id: UUID,
    message_id: str,
    content: str,
    response_content: Optional[str] = None,
    response_time: Optional[int] = None,
    delivery_status: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """Log message-specific interaction details."""
    scoring_service = LeadScoringService(db)
    try:
        # First create the base interaction
        interaction = scoring_service.log_interaction(
            lead_id=lead_id,
            customer_id=current_user.customer_id,
            interaction_type="message",
            status="success"
        )
        # Then log message-specific details
        message_interaction = scoring_service.log_message_interaction(
            interaction_id=interaction.id,
            message_id=message_id,
            content=content,
            response_content=response_content,
            response_time=response_time,
            delivery_status=delivery_status
        )
        # Update lead score
        scoring_service.update_lead_score(lead_id)
        return message_interaction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/new/", response_model=LeadResponse)
async def create_lead_new(
    *,
    db: Session = Depends(deps.get_db),
    lead_in: LeadCreate,
    current_user = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """Create a new lead for the current customer (new endpoint)."""
    lead_service = LeadService(db)
    return await lead_service.create_lead(lead_in, current_customer.id)

@router.put("/edit/{lead_id}", response_model=LeadResponse)
async def update_lead_new(
    *,
    db: Session = Depends(deps.get_db),
    lead_id: int,
    lead_in: LeadUpdate,
    current_user = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """Update a lead for the current customer (new endpoint)."""
    lead_service = LeadService(db)
    return await lead_service.update_lead(lead_id, lead_in, current_customer.id)

@router.get("/", response_model=LeadListResponse)
async def list_leads(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer),
    filter_params: LeadFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> Any:
    """List leads with optional filtering."""
    lead_service = LeadService(db)
    leads = await lead_service.list_leads(
        customer_id=str(current_customer.id),
        filter_params=filter_params,
        skip=skip,
        limit=limit
    )
    total = len(leads)  # In a real app, you'd want to get the total count from the database
    return {"items": leads, "total": total}

@router.post("/{lead_id}/activities", response_model=LeadActivityResponse)
async def create_lead_activity(
    *,
    db: Session = Depends(get_db),
    lead_id: int,
    activity_in: LeadActivityCreate,
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> Any:
    """Create a new activity for a lead."""
    lead_service = LeadService(db)
    try:
        lead = await lead_service.get_lead(
            lead_id=lead_id,
            customer_id=str(current_customer.id)
        )
        activity = await lead_service._log_activity(
            lead=lead,
            user_id=str(current_user.id),
            activity_type=activity_in.activity_type,
            description=activity_in.description
        )
        return activity
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{lead_id}/activities", response_model=List[LeadActivityResponse])
async def list_lead_activities(
    *,
    db: Session = Depends(get_db),
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> Any:
    """List all activities for a lead."""
    lead_service = LeadService(db)
    try:
        lead = await lead_service.get_lead(
            lead_id=lead_id,
            customer_id=str(current_customer.id)
        )
        return lead.activities
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{lead_id}/assign", response_model=LeadResponse)
async def assign_lead(
    *,
    db: Session = Depends(get_db),
    lead_id: int,
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> Any:
    """Assign a lead to a user."""
    lead_service = LeadService(db)
    try:
        lead = await lead_service.assign_lead(
            lead_id=lead_id,
            user_id=user_id,
            assigned_by=str(current_user.id),
            customer_id=str(current_customer.id)
        )
        return lead
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/stats", response_model=LeadStats)
async def get_lead_stats(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
) -> Any:
    """Get lead statistics."""
    lead_service = LeadService(db)
    return await lead_service.get_lead_stats(customer_id=str(current_customer.id)) 