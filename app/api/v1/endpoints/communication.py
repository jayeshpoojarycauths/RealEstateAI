from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.api import deps
from app.schemas.communication import (
    CommunicationPreferences,
    CommunicationPreferencesCreate,
    CommunicationPreferencesUpdate,
    CommunicationChannel,
    CommunicationPreferencesResponse
)
from app.services.communication import CommunicationService
from app.models.models import User, Lead, Customer, CommunicationPreferences, CommunicationChannel
from app.core.deps import get_current_active_user
from pydantic import BaseModel
from uuid import UUID
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

class SendMessageRequest(BaseModel):
    message: str
    channel: CommunicationChannel

@router.get("/preferences", response_model=CommunicationPreferencesResponse)
async def get_communication_preferences(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
) -> CommunicationPreferencesResponse:
    """Get communication preferences for the current customer."""
    communication_service = CommunicationService(db, current_customer)
    preferences = await communication_service.get_communication_preferences(current_customer.id)
    if not preferences:
        raise HTTPException(status_code=404, detail="Communication preferences not found")
    return preferences

@router.post("/preferences", response_model=CommunicationPreferencesResponse)
async def create_communication_preferences(
    preferences: CommunicationPreferencesCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
) -> CommunicationPreferencesResponse:
    """Create communication preferences for the current customer."""
    communication_service = CommunicationService(db, current_customer)
    return await communication_service.create_communication_preferences(
        customer_id=current_customer.id,
        preferences=preferences
    )

@router.put("/preferences", response_model=CommunicationPreferencesResponse)
async def update_communication_preferences(
    preferences: CommunicationPreferencesUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
) -> CommunicationPreferencesResponse:
    """Update communication preferences for the current customer."""
    communication_service = CommunicationService(db, current_customer)
    return await communication_service.update_communication_preferences(
        customer_id=current_customer.id,
        preferences=preferences
    )

@router.post("/send/{lead_id}/")
async def send_message(
    lead_id: UUID,
    request: SendMessageRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """
    Send a message to a lead through the specified channel.
    """
    logger.info(f"Received request to send message to lead {lead_id}")
    logger.info(f"Message: {request.message}")
    logger.info(f"Channel: {request.channel}")
    
    # Get lead
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.customer_id == current_user.customer_id
    ).first()
    
    if not lead:
        logger.error(f"Lead {lead_id} not found")
        raise HTTPException(status_code=404, detail="Lead not found")
    
    logger.info(f"Found lead: {lead.id}, name: {lead.name}")
    logger.info(f"Original phone number: {lead.phone}")
    
    # Validate lead has a phone number
    if not lead.phone:
        logger.error(f"Lead {lead_id} has no phone number")
        raise HTTPException(status_code=400, detail="Lead has no phone number")
    
    # Format phone number if needed
    phone_number = str(lead.phone).strip()
    logger.info(f"Stripped phone number: {phone_number}")
    
    if not phone_number.startswith('+'):
        phone_number = f"+91{phone_number}"  # Add India country code if not present
        logger.info(f"Added country code. New phone number: {phone_number}")
    
    # Update lead's phone number with formatted version
    lead.phone = phone_number
    logger.info(f"Updated lead phone number to: {lead.phone}")
    
    # Send message
    comm_service = CommunicationService(db, current_customer)
    try:
        logger.info("Attempting to send message through communication service")
        result = await comm_service.send_message(lead, request.message, request.channel)
        logger.info(f"Message sent successfully. Result: {result}")
        return {"status": "success", "details": result}
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-bulk/")
def send_bulk_messages(
    lead_ids: List[int],
    message: str,
    channel: CommunicationChannel,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    current_customer: Customer = Depends(deps.get_current_customer)
):
    """
    Send a message to multiple leads through the specified channel.
    """
    comm_service = CommunicationService(db, current_customer)
    results = []
    errors = []
    
    for lead_id in lead_ids:
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.customer_id == current_user.customer_id
        ).first()
        
        if not lead:
            errors.append(f"Lead {lead_id} not found")
            continue
        
        try:
            result = comm_service.send_message(lead, message, channel)
            results.append({"lead_id": lead_id, "status": "success", "details": result})
        except Exception as e:
            errors.append(f"Lead {lead_id}: {str(e)}")
    
    return {
        "total_leads": len(lead_ids),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    } 