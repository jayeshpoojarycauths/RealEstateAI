from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from uuid import UUID
import pandas as pd
from io import BytesIO

from app.shared.models.user import User
from app.shared.db.session import get_db
from app.shared.core.security.auth import get_current_customer
from app.lead.models import Lead
from app.shared.models.customer import Customer
from app.outreach.models.outreach import OutreachLog

from app.shared.core.communication import OutreachEngine
from app.shared.core.auth import get_current_user
from app.outreach.schemas.outreach import (
    OutreachCreate, Outreach, OutreachFilter,
    OutreachStats, OutreachAnalytics, OutreachRequest, OutreachLogResponse, LeadUpload, OutreachChannel, OutreachStatus,
    InteractionLogCreate, InteractionLogResponse,
    OutreachUpdate, OutreachTemplate, OutreachTemplateCreate, OutreachTemplateUpdate,
    CommunicationPreference, CommunicationPreferenceCreate, CommunicationPreferenceUpdate,
    OutreachList, OutreachTemplateList, OutreachTemplateFilter
)
from app.outreach.services.outreach import OutreachService
from app.shared.core.pagination import PaginationParams, get_pagination_params
from app.shared.core.security.dependencies import require_role
from app.shared.core.security.roles import Role as UserRole
from app.shared.core.outreach import MockOutreachEngine
from datetime import datetime

router = APIRouter()

@router.post("/leads/{lead_id}/outreach")
async def initiate_outreach(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    lead_id: UUID,
) -> Any:
    """
    Initiate outreach to a lead through configured channels
    """
    # Get lead
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.customer_id == current_user.customer_id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    # Get communication preferences
    preferences = db.query(CommunicationPreferences).filter(
        CommunicationPreferences.customer_id == current_user.customer_id
    ).first()

    if not preferences:
        raise HTTPException(
            status_code=400,
            detail="Communication preferences not configured"
        )

    
    # Initialize communication service
    comm_service = OutreachEngine(preferences)

    # Send messages through all enabled channels
    results = await comm_service.send_all_channels(lead)

    # Log outreach attempts
    for channel, success in results.items():
        log = OutreachLog(
            lead_id=lead.id,
            customer_id=current_user.customer_id,
            channel=channel,
            status="success" if success else "failed",
            message=f"Outreach attempt via {channel}"
        )
        db.add(log)
    
    db.commit()

    return {
        "message": "Outreach initiated",
        "results": results
    }

@router.post("/leads/bulk-outreach")
async def initiate_bulk_outreach(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    lead_ids: List[UUID],
) -> Any:
    """
    Initiate outreach to multiple leads
    """
    # Get communication preferences
    preferences = db.query(CommunicationPreferences).filter(
        CommunicationPreferences.customer_id == current_user.customer_id
    ).first()

    if not preferences:
        raise HTTPException(
            status_code=400,
            detail="Communication preferences not configured"
        )

    # Initialize communication service
    comm_service = OutreachEngine(preferences)

    results = []
    for lead_id in lead_ids:
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.customer_id == current_user.customer_id
        ).first()

        if lead:
            channel_results = await comm_service.send_all_channels(lead)
            
            # Log outreach attempts
            for channel, success in channel_results.items():
                log = OutreachLog(
                    lead_id=lead.id,
                    customer_id=current_user.customer_id,
                    channel=channel,
                    status="success" if success else "failed",
                    message=f"Outreach attempt via {channel}"
                )
                db.add(log)
            
            results.append({
                "lead_id": str(lead_id),
                "results": channel_results
            })

    db.commit()

    return {
        "message": "Bulk outreach initiated",
        "results": results
    }

@router.post("/leads/{lead_id}", response_model=Outreach)
@require_role([UserRole.ADMIN, UserRole.AGENT])
async def trigger_outreach(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Trigger AI outreach for a specific lead.
    Uses mock engine to simulate different communication channels.
    """
    # Get lead
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.customer_id == current_user.customer_id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    try:
        # Get communication preferences
        preferences = db.query(CommunicationPreferences).filter(
            CommunicationPreferences.customer_id == current_user.customer_id
        ).first()

        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No communication preferences found"
            )

        # Initialize mock engine
        engine = MockOutreachEngine(preferences)

        # Create outreach record
        outreach = Outreach(
            lead_id=lead_id,
            channel=preferences.default_channel,
            message=engine.generate_message(lead),
            status="scheduled",
            customer_id=current_user.customer_id
        )
        db.add(outreach)
        db.flush()

        # Simulate outreach
        result = engine.send(outreach)

        # Update outreach status
        outreach.status = result.status
        outreach.updated_at = datetime.utcnow()

        # Log interaction
        interaction = InteractionLog(
            lead_id=lead_id,
            outreach_id=outreach.id,
            channel=outreach.channel,
            status=result.status,
            response_time=result.response_time,
            customer_id=current_user.customer_id
        )
        db.add(interaction)

        db.commit()

        return Outreach(
            id=outreach.id,
            lead_id=lead_id,
            channel=outreach.channel,
            message=outreach.message,
            status=outreach.status,
            created_at=outreach.created_at,
            updated_at=outreach.updated_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[Outreach])
async def list_outreach(
    pagination: PaginationParams = Depends(get_pagination_params),
    filters: OutreachFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List outreach attempts with pagination and filtering.
    """
    outreach_service = OutreachService(db)
    outreach_list = await outreach_service.list_outreach(
        customer_id=current_user.customer_id,
        pagination=pagination,
        filters=filters
    )
    return outreach_list

@router.get("/leads/{lead_id}", response_model=List[Outreach])
async def get_lead_outreach(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all outreach attempts for a specific lead.
    """
    outreach_service = OutreachService(db)
    outreach_list = await outreach_service.get_lead_outreach(
        lead_id, current_user.customer_id
    )
    if not outreach_list:
        raise HTTPException(status_code=404, detail="Lead not found")
    return outreach_list

@router.get("/stats", response_model=OutreachStats)
async def get_outreach_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get outreach statistics.
    """
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        # Query logs
        query = db.query(OutreachLog).filter(
            OutreachLog.customer_id == current_user.customer_id
        )

        if start:
            query = query.filter(OutreachLog.created_at >= start)
        if end:
            query = query.filter(OutreachLog.created_at <= end)

        # Calculate stats
        total_outreach = query.count()
        successful_outreach = query.filter(OutreachLog.status == "sent").count()
        failed_outreach = query.filter(OutreachLog.status == "failed").count()

        # Calculate channel distribution
        channel_stats = {}
        for channel in OutreachChannel:
            count = query.filter(OutreachLog.channel == channel).count()
            if count > 0:
                channel_stats[channel.value] = count

        return OutreachStats(
            total_outreach=total_outreach,
            successful_outreach=successful_outreach,
            failed_outreach=failed_outreach,
            channel_distribution=channel_stats
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating stats: {str(e)}"
        )

@router.get("/analytics", response_model=OutreachAnalytics)
async def get_outreach_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed outreach analytics.
    """
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        # Query logs
        query = db.query(OutreachLog).filter(
            OutreachLog.customer_id == current_user.customer_id
        )

        if start:
            query = query.filter(OutreachLog.created_at >= start)
        if end:
            query = query.filter(OutreachLog.created_at <= end)

        # Calculate daily outreach volume
        daily_volume = {}
        for log in query.order_by(OutreachLog.created_at):
            date = log.created_at.date().isoformat()
            daily_volume[date] = daily_volume.get(date, 0) + 1

        # Calculate success rate by channel
        channel_success = {}
        for channel in OutreachChannel:
            channel_query = query.filter(OutreachLog.channel == channel)
            total = channel_query.count()
            if total > 0:
                successful = channel_query.filter(OutreachLog.status == "sent").count()
                channel_success[channel.value] = (successful / total) * 100

        return OutreachAnalytics(
            daily_outreach_volume=daily_volume,
            channel_success_rate=channel_success
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating analytics: {str(e)}"
        )

@router.post("/leads/{lead_id}/schedule", response_model=Outreach)
async def schedule_outreach(
    lead_id: int,
    outreach: OutreachCreate,
    schedule_time: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Schedule an outreach to a lead for a specific time.
    """
    outreach_service = OutreachService(db)
    result = await outreach_service.schedule_outreach(
        lead_id, outreach, schedule_time, current_user.customer_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    return result

@router.delete("/leads/{lead_id}/schedule/{outreach_id}")
async def cancel_scheduled_outreach(
    lead_id: int,
    outreach_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a scheduled outreach.
    """
    outreach_service = OutreachService(db)
    success = await outreach_service.cancel_scheduled_outreach(
        lead_id, outreach_id, current_user.customer_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Outreach not found")
    return {"message": "Scheduled outreach cancelled successfully"}

@router.post("/upload", response_model=List[LeadUpload])
async def upload_leads(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    Upload leads from CSV/Excel file and validate data.
    """
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and Excel files are supported"
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
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        # Convert to list of LeadUpload objects
        leads = []
        for _, row in df.iterrows():
            lead = LeadUpload(
                name=row['name'],
                email=row.get('email'),
                phone=row.get('phone'),
                source=row['source'],
                notes=row.get('notes'),
                property_preferences=row.get('property_preferences'),
                budget_range=row.get('budget_range')
            )
            leads.append(lead)

        return leads

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file: {str(e)}"
        )

@router.post("/send", response_model=List[OutreachLogResponse])
async def send_outreach(
    request: OutreachRequest,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    Send outreach messages to leads via specified channel.
    """
    try:
        # Initialize outreach service
        outreach_service = OutreachService(db, current_customer)

        # Send outreach messages
        logs = await outreach_service.send_outreach(
            channel=request.channel,
            leads=request.leads
        )

        # Convert logs to response model
        return [
            OutreachLogResponse(
                id=log.id,
                lead_id=log.lead_id,
                channel=log.channel,
                status=log.status,
                message=log.message,
                sent_at=log.sent_at,
                created_at=log.created_at
            )
            for log in logs
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending outreach: {str(e)}"
        )

@router.get("/logs", response_model=List[OutreachLogResponse])
async def get_outreach_logs(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
    skip: int = 0,
    limit: int = 100
):
    """
    Get outreach logs for the current customer.
    """
    outreach_service = OutreachService(db, current_customer)
    logs = outreach_service.get_logs(skip=skip, limit=limit)
    
    return [
        OutreachLogResponse(
            id=log.id,
            lead_id=log.lead_id,
            channel=log.channel,
            status=log.status,
            message=log.message,
            sent_at=log.sent_at,
            created_at=log.created_at
        )
        for log in logs
    ]

@router.post("/outreach", response_model=Outreach)
def create_outreach(
    outreach: OutreachCreate,
    db: Session = Depends(get_db)
) -> Outreach:
    """Create a new outreach attempt."""
    service = OutreachService(db)
    return service.create_outreach(outreach)

@router.get("/outreach/{outreach_id}", response_model=Outreach)
def get_outreach(
    outreach_id: UUID,
    db: Session = Depends(get_db)
) -> Outreach:
    """Get an outreach attempt by ID."""
    service = OutreachService(db)
    return service.get_outreach(outreach_id)

@router.put("/outreach/{outreach_id}", response_model=Outreach)
def update_outreach(
    outreach_id: UUID,
    outreach: OutreachUpdate,
    db: Session = Depends(get_db)
) -> Outreach:
    """Update an outreach attempt."""
    service = OutreachService(db)
    return service.update_outreach(outreach_id, outreach)

@router.get("/outreach", response_model=OutreachList)
def list_outreach(
    channel: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
) -> OutreachList:
    """List outreach attempts with filtering."""
    service = OutreachService(db)
    filter_params = OutreachFilter(
        channel=channel,
        status=status,
        start_date=start_date,
        end_date=end_date,
        search=search
    )
    items = service.list_outreach(filter_params)
    return OutreachList(items=items, total=len(items))

@router.post("/templates", response_model=OutreachTemplate)
def create_template(
    template: OutreachTemplateCreate,
    db: Session = Depends(get_db)
) -> OutreachTemplate:
    """Create a new outreach template."""
    service = OutreachService(db)
    return service.create_template(template)

@router.get("/templates/{template_id}", response_model=OutreachTemplate)
def get_template(
    template_id: UUID,
    db: Session = Depends(get_db)
) -> OutreachTemplate:
    """Get a template by ID."""
    service = OutreachService(db)
    return service.get_template(template_id)

@router.put("/templates/{template_id}", response_model=OutreachTemplate)
def update_template(
    template_id: UUID,
    template: OutreachTemplateUpdate,
    db: Session = Depends(get_db)
) -> OutreachTemplate:
    """Update a template."""
    service = OutreachService(db)
    return service.update_template(template_id, template)

@router.get("/templates", response_model=OutreachTemplateList)
async def list_templates(
    channel: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> OutreachTemplateList:
    """List templates with filtering."""
    service = OutreachService(db)
    filter_params = OutreachTemplateFilter(
        channel=channel,
        is_active=is_active
    )
    return await service.list_templates(filter_params)

@router.post("/preferences", response_model=CommunicationPreference)
def create_communication_preference(
    preference: CommunicationPreferenceCreate,
    db: Session = Depends(get_db)
) -> CommunicationPreference:
    """Create communication preferences for a customer."""
    service = OutreachService(db)
    return service.create_communication_preference(preference)

@router.get("/preferences/{customer_id}", response_model=CommunicationPreference)
def get_communication_preference(
    customer_id: UUID,
    db: Session = Depends(get_db)
) -> CommunicationPreference:
    """Get communication preferences for a customer."""
    service = OutreachService(db)
    return service.get_communication_preference(customer_id)

@router.put("/preferences/{customer_id}", response_model=CommunicationPreference)
def update_communication_preference(
    customer_id: UUID,
    preference: CommunicationPreferenceUpdate,
    db: Session = Depends(get_db)
) -> CommunicationPreference:
    """Update communication preferences for a customer."""
    service = OutreachService(db)
    return service.update_communication_preference(customer_id, preference)

@router.get("/stats", response_model=OutreachStats)
def get_outreach_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
) -> OutreachStats:
    """Get outreach statistics."""
    service = OutreachService(db)
    return service.get_outreach_stats(start_date, end_date)

@router.get("/analytics", response_model=OutreachAnalytics)
def get_outreach_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
) -> OutreachAnalytics:
    """Get detailed outreach analytics."""
    service = OutreachService(db)
    return service.get_outreach_analytics(days) 