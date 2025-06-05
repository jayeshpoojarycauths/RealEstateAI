from typing import Optional, Dict, Any, List
from datetime import datetime
from app.shared.core.exceptions import ExternalServiceError
from abc import ABC, abstractmethod
import logging

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class OutreachEngine(ABC):
    """
    Abstract base class for outreach engines.
    """
    @abstractmethod
    async def send_outreach(
        self,
        channel: str,
        recipient: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send an outreach message through the specified channel.
        
        Args:
            channel: The communication channel to use (e.g., 'email', 'sms', 'call')
            recipient: The recipient's contact information
            message: The message content to send
            metadata: Additional metadata for the outreach
            
        Returns:
            Dict containing the outreach result
        """
        pass

class MockOutreachEngine(OutreachEngine):
    """
    Mock implementation of the outreach engine for testing.
    """
    def __init__(self, db: Session):
        self.db = db
        self.outreach_history = []

    async def send_outreach(
        self,
        channel: str,
        recipient: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Mock implementation that logs the outreach attempt.
        """
        logger.info(
            f"Mock outreach sent - Channel: {channel}, "
            f"Recipient: {recipient}, Message: {message}"
        )
        
        outreach_record = {
            "status": "success",
            "channel": channel,
            "recipient": recipient,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.outreach_history.append(outreach_record)
        return outreach_record

    async def get_outreach_history(
        self,
        lead_id: int,
        customer_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Mock implementation of get_outreach_history."""
        return [
            record for record in self.outreach_history
            if record["lead_id"] == lead_id
            and (customer_id is None or record["customer_id"] == customer_id)
        ]

    async def schedule_outreach(
        self,
        lead_id: int,
        channel: str,
        message: str,
        scheduled_time: datetime,
        customer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Mock implementation of schedule_outreach."""
        outreach_record = {
            "lead_id": lead_id,
            "channel": channel,
            "message": message,
            "customer_id": customer_id,
            "scheduled_time": scheduled_time.isoformat(),
            "status": "scheduled"
        }
        self.outreach_history.append(outreach_record)
        return outreach_record

class OutreachService:
    """Service for handling outreach activities."""
    
    def __init__(self, db: Session):
        self.db = db
        self.engine = MockOutreachEngine(db)

    async def send_outreach(
        self,
        lead_id: int,
        channel: str,
        message: str,
        customer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send outreach message to a lead.
        
        Args:
            lead_id: ID of the lead to contact
            channel: Communication channel (email, sms, etc.)
            message: Message content
            customer_id: Optional customer ID for tracking
            
        Returns:
            Dict containing outreach details and status
        """
        return await self.engine.send_outreach(lead_id, channel, message, customer_id)

    async def get_outreach_history(
        self,
        lead_id: int,
        customer_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get outreach history for a lead.
        
        Args:
            lead_id: ID of the lead
            customer_id: Optional customer ID for filtering
            
        Returns:
            List of outreach activities
        """
        return await self.engine.get_outreach_history(lead_id, customer_id)

    async def schedule_outreach(
        self,
        lead_id: int,
        channel: str,
        message: str,
        scheduled_time: datetime,
        customer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Schedule an outreach message.
        
        Args:
            lead_id: ID of the lead to contact
            channel: Communication channel
            message: Message content
            scheduled_time: When to send the message
            customer_id: Optional customer ID for tracking
            
        Returns:
            Dict containing scheduling details
        """
        return await self.engine.schedule_outreach(
            lead_id, channel, message, scheduled_time, customer_id
        )

__all__ = [
    "OutreachEngine",
    "MockOutreachEngine"
] 