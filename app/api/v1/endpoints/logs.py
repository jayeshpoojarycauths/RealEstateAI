from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from app.api.deps import get_db
from app.core.logging import logger, log_request, log_error
from app.core.messages import MessageCode
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class FrontendLogEntry(BaseModel):
    """Model for frontend log entries."""
    level: str
    message: str
    timestamp: datetime
    context: Dict[str, Any]
    stack_trace: Optional[str] = None

class FrontendLogBatch(BaseModel):
    """Model for batch of frontend log entries."""
    logs: List[FrontendLogEntry]

@router.post("/client")
async def log_client_event(
    request: Request,
    log_batch: FrontendLogBatch,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Endpoint for receiving and processing frontend logs.
    
    Args:
        request: FastAPI request object
        log_batch: Batch of log entries from frontend
        db: Database session
        
    Returns:
        Dict with processing status
    """
    try:
        for log_entry in log_batch.logs:
            # Map frontend log levels to backend levels and message codes
            level = log_entry.level.upper()
            if level == "ERROR":
                log_error(
                    logger=logger,
                    request=request,
                    message_code=MessageCode.SYSTEM_ERROR,
                    error=Exception(log_entry.message),
                    frontend_context=log_entry.context,
                    stack_trace=log_entry.stack_trace
                )
            else:
                # Map log levels to message codes
                if level == "INFO":
                    message_code = MessageCode.AUTH_MFA_REQUIRED  # Example info code
                elif level == "WARN" or level == "WARNING":
                    message_code = MessageCode.AUTH_REGISTER_FAILED  # Example warning code
                elif level == "DEBUG":
                    message_code = MessageCode.AUTH_LOGIN_SUCCESS  # Example debug code
                else:
                    message_code = MessageCode.SYSTEM_ERROR  # Fallback
                log_request(
                    logger=logger,
                    request=request,
                    message_code=message_code,
                    frontend_level=level,
                    frontend_message=log_entry.message,
                    frontend_context=log_entry.context
                )
        
        return {
            "status": "success",
            "message": "Logs processed successfully",
            "count": len(log_batch.logs)
        }
        
    except Exception as e:
        log_error(
            logger=logger,
            request=request,
            message_code=MessageCode.SYSTEM_ERROR,
            error=e
        )
        raise 