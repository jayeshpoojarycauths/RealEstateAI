from typing import Optional, Dict, Any, List
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.shared.core.config import settings
from app.shared.core.infrastructure.logging import logger
from app.shared.core.exceptions import RateLimitException, ExternalServiceError
import logging
from datetime import datetime, timedelta
from ratelimit import limits, sleep_and_retry
import asyncio
from app.lead.models.lead import Lead
from app.shared.models.customer import Customer
from sqlalchemy.orm import Session
import os

logger = logging.getLogger(__name__)

async def send_mfa_code_sms(
    phone_number: str,
    code: str,
    customer_id: Optional[int] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Standalone function to send MFA verification code via SMS.
    
    Args:
        phone_number: Recipient phone number
        code: MFA verification code
        customer_id: Optional customer ID for tracking
        db: Optional database session
        
    Returns:
        Dict containing message details and status
    """
    sms_service = SMSService(db) if db else SMSService(None)
    return await sms_service.send_mfa_code_sms(phone_number, code, customer_id)

class SMSService:
    def __init__(self, db: Session):
        """Initialize SMS service with Twilio client."""
        self.db = db
        try:
            self.client = Client(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            )
            self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
            logger.info("SMS service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SMS service: {str(e)}")
            raise SMSError("Failed to initialize SMS service")

    async def send_mfa_code_sms(
        self,
        phone_number: str,
        code: str,
        customer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send MFA verification code via SMS.
        
        Args:
            phone_number: Recipient phone number
            code: MFA verification code
            customer_id: Optional customer ID for tracking
            
        Returns:
            Dict containing message details and status
        """
        message = f"Your verification code is: {code}. This code will expire in 10 minutes."
        return await self.send_sms(phone_number, message, customer_id)

    @sleep_and_retry
    @limits(calls=100, period=60)  # 100 calls per minute
    async def send_sms(
        self,
        to_number: str,
        message: str,
        customer_id: Optional[int] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Send an SMS message using Twilio with rate limiting and retries.
        
        Args:
            to_number: The recipient's phone number
            message: The message content
            customer_id: Optional customer ID for tracking
            retry_count: Number of retry attempts
            
        Returns:
            Dict containing message details and status
            
        Raises:
            SMSError: If message sending fails
            RateLimitError: If rate limit is exceeded
        """
        try:
            logger.info(f"Sending SMS to {to_number} for customer {customer_id}")
            
            # Validate phone number format
            if not self._validate_phone_number(to_number):
                raise SMSError(f"Invalid phone number format: {to_number}")

            # Check message length
            if len(message) > 1600:  # Twilio's limit
                raise SMSError("Message exceeds maximum length of 1600 characters")

            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully. Message SID: {message.sid}")
            
            return {
                "status": "success",
                "message_id": message.sid,
                "to": to_number,
                "customer_id": customer_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS: {str(e)}")
            
            # Handle specific Twilio error codes
            if e.code == 21211:  # Invalid phone number
                raise SMSError(f"Invalid phone number: {to_number}")
            elif e.code == 21608:  # Rate limit exceeded
                raise RateLimitException("SMS rate limit exceeded")
            elif e.code == 21614:  # Unreachable number
                raise SMSError(f"Phone number {to_number} is unreachable")
            
            # Retry on certain error codes
            if retry_count < 3 and e.code in [20003, 20008, 20012]:  # Retryable errors
                logger.warning(f"Retrying SMS send. Attempt {retry_count + 1}")
                return await self.send_sms(to_number, message, customer_id, retry_count + 1)
            
            raise SMSError(f"Failed to send SMS: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            raise SMSError(f"Failed to send SMS: {str(e)}")

    async def send_bulk_sms(
        self,
        numbers: List[str],
        message: str,
        customer_id: Optional[int] = None,
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Send SMS messages to multiple recipients with batching and error handling.
        
        Args:
            numbers: List of recipient phone numbers
            message: The message content
            customer_id: Optional customer ID for tracking
            batch_size: Number of messages to send in each batch
            
        Returns:
            Dict containing results for each message
        """
        results = []
        errors = []
        start_time = datetime.utcnow()
        
        logger.info(f"Starting bulk SMS send to {len(numbers)} recipients")
        
        # Process in batches to avoid overwhelming the API
        for i in range(0, len(numbers), batch_size):
            batch = numbers[i:i + batch_size]
            batch_results = []
            
            for number in batch:
                try:
                    result = await self.send_sms(number, message, customer_id)
                    batch_results.append(result)
                except (SMSError, RateLimitException) as e:
                    logger.error(f"Error sending SMS to {number}: {str(e)}")
                    errors.append({
                        "number": number,
                        "error": str(e)
                    })
                    batch_results.append({
                        "status": "error",
                        "to": number,
                        "error": str(e)
                    })
            
            results.extend(batch_results)
            
            # Add delay between batches to respect rate limits
            if i + batch_size < len(numbers):
                await asyncio.sleep(1)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "status": "completed",
            "total_messages": len(numbers),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "errors": errors,
            "duration_seconds": duration,
            "results": results
        }

    def _validate_phone_number(self, number: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            number: Phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Remove any non-digit characters
        digits = ''.join(filter(str.isdigit, number))
        
        # Basic validation (can be enhanced based on requirements)
        return len(digits) >= 10 and len(digits) <= 15 

class SMSError(Exception):
    """Base exception for SMS-related errors"""
    pass 