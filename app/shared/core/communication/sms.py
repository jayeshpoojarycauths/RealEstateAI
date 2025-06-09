import logging

from app.shared.core.exceptions import ExternalServiceError
from app.shared.core.sms import SMSService
from app.shared.core.logging import logger
from app.shared.core.logging import logger

logger = logging.getLogger(__name__)

async def send_sms(
    phone_number: str,
    message: str
) -> None:
    """Send an SMS message."""
    try:
        # TODO: Implement actual SMS sending logic
        # For now, just log the message
        logger.info(f"Sending SMS to {phone_number}: {message}")
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        raise ExternalServiceError("Failed to send SMS")

async def send_verification_sms(
    phone_number: str,
    code: str
) -> None:
    """Send verification SMS."""
    message = f"Your verification code is: {code}"
    await send_sms(phone_number, message)

async def send_password_reset_sms(
    phone_number: str,
    code: str
) -> None:
    """Send password reset SMS."""
    message = f"Your password reset code is: {code}"
    await send_sms(phone_number, message)

__all__ = [
    'send_sms',
    'send_verification_sms',
    'send_password_reset_sms',
    'SMSService',
] 