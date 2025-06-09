"""
CAPTCHA verification utilities.
"""

import logging
from typing import Optional

from fastapi import HTTPException, Request
from pydantic import BaseModel

from app.shared.core.config import settings

# Get logger directly from logging module
logger = logging.getLogger("app")

class CaptchaResponse(BaseModel):
    """CAPTCHA response model."""
    success: bool
    score: Optional[float] = None
    action: Optional[str] = None
    challenge_ts: Optional[str] = None
    hostname: Optional[str] = None
    error_codes: Optional[list[str]] = None

async def verify_captcha(request: Request) -> None:
    """
    Verify CAPTCHA token from request.
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: If CAPTCHA verification fails
    """
    if not settings.ENABLE_CAPTCHA:
        return

    try:
        token = request.headers.get("X-Captcha-Token")
        if not token:
            raise HTTPException(status_code=400, detail="CAPTCHA token required")

        # TODO: Implement actual CAPTCHA verification
        # For now, just log the attempt
        logger.info("CAPTCHA verification requested", extra={
            "token": token[:10] + "..." if token else None,
            "ip": request.client.host if request.client else None
        })

    except Exception as e:
        logger.error("CAPTCHA verification failed", extra={
            "error": str(e),
            "ip": request.client.host if request.client else None
        })
        raise HTTPException(status_code=400, detail="CAPTCHA verification failed")

__all__ = ["verify_captcha", "CaptchaResponse"] 