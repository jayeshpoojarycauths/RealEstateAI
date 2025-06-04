from typing import Optional, Dict, Any, List
from datetime import datetime
from app.shared.core.exceptions import ExternalServiceError

from sqlalchemy.orm import Session

class MockOutreachEngine:
    """Mock implementation of outreach engine for testing."""
    
    def __init__(self, db: Session):
        self.db = db
        self.outreach_history = []

    async def send_outreach(
        self,
        lead_id: int,
        channel: str,
        message: str,
        customer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Mock implementation of send_outreach."""
        # Record the outreach attempt
        outreach_record = {
            "lead_id": lead_id,
            "channel": channel,
            "message": message,
            "customer_id": customer_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
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