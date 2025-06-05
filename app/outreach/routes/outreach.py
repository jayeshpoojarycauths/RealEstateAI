from app.shared.models.interaction import CallInteraction
from app.shared.core.security.auth import get_current_active_user
from app.shared.core.exceptions import ExternalServiceError

@router.post("/call-status")
async def call_status_callback(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Handle Twilio call status callbacks.
    """
    try:
        # Get form data from Twilio
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")
        recording_url = form_data.get("RecordingUrl")
        recording_sid = form_data.get("RecordingSid")
        duration = form_data.get("CallDuration")
        error_code = form_data.get("ErrorCode")
        error_message = form_data.get("ErrorMessage")

        # Find the call interaction
        call_interaction = db.query(CallInteraction).filter(
            CallInteraction.call_sid == call_sid
        ).first()

        if not call_interaction:
            raise HTTPException(
                status_code=404,
                detail=f"Call interaction not found for SID: {call_sid}"
            )

        # Update call interaction
        call_interaction.status = call_status
        if recording_url:
            call_interaction.recording_url = recording_url
        if duration:
            call_interaction.duration = int(duration)
        
        # Update call quality metrics
        call_interaction.call_quality_metrics.update({
            "status": call_status,
            "error_code": error_code,
            "error_message": error_message,
            "recording_sid": recording_sid,
            "updated_at": datetime.utcnow().isoformat()
        })

        db.commit()

        # Log the status update
        await AuditLogger(db, current_user.customer).log(
            action="call_status_updated",
            resource_type="call",
            resource_id=call_sid,
            details={
                "status": call_status,
                "recording_url": recording_url,
                "duration": duration,
                "error_code": error_code,
                "error_message": error_message
            }
        )

        return {
            "status": "success",
            "message": f"Call status updated to {call_status}",
            "call_sid": call_sid
        }

    except Exception as e:
        logger.error(f"Error processing call status callback: {str(e)}")
        raise ExternalServiceError(
            message="Failed to process call status callback",
            details=str(e)
        ) 