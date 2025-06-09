import asyncio
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.lead.models.lead import Lead
from app.outreach.models.outreach import CommunicationPreference
from app.shared.core.exceptions import ServiceUnavailableException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict
from typing import Any
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict
from typing import Any


class OutreachResult:
    """Result of an outreach attempt."""
    def __init__(self, status: str, response_time: Optional[float] = None):
        self.status = status
        self.response_time = response_time

class MockOutreachEngine:
    """Mock implementation of outreach engine for testing."""
    
    def __init__(self, db: Session, preferences: Optional[CommunicationPreference] = None):
        self.db = db
        self.preferences = preferences
        self.outreach_history = []
        self.channel_templates = {
            'email': {
                'subject': 'Interested in {project_name}?',
                'body': 'Hi {name},\n\nI noticed you were interested in {project_name}. Would you like to schedule a viewing?\n\nBest regards,\n{agent_name}'
            },
            'sms': {
                'body': 'Hi {name}, interested in {project_name}? Reply YES to schedule a viewing.'
            },
            'whatsapp': {
                'body': 'Hi {name}! 👋 I noticed you were interested in {project_name}. Would you like to schedule a viewing?'
            },
            'telegram': {
                'body': 'Hi {name}! I noticed you were interested in {project_name}. Would you like to schedule a viewing?'
            }
        }

    def generate_message(self, lead: Lead, channel: str) -> str:
        """Generate a message based on the lead and channel."""
        template = self.channel_templates.get(channel, {})

        if channel == 'email':
            return template['body'].format(
                name=lead.name,
                project_name='our latest project',
                agent_name='Your Agent'
            )
        else:
            return template['body'].format(
                name=lead.name,
                project_name='our latest project'
            )

    async def send_outreach(
        self,
        lead_id: int,
        channel: str,
        message: str,
        customer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send an outreach message."""
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Simulate success/failure
        success_rate = {
            'email': 0.95,
            'sms': 0.90,
            'whatsapp': 0.85,
            'telegram': 0.80
        }.get(channel, 0.90)

        status = 'delivered' if random.random() < success_rate else 'failed'
        response_time = random.uniform(1.0, 24.0) if status == 'delivered' else None

        # Record the outreach attempt
        outreach_record = {
            "lead_id": lead_id,
            "channel": channel,
            "message": message,
            "customer_id": customer_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "response_time": response_time
        }
        self.outreach_history.append(outreach_record)
        return outreach_record

    async def get_outreach_history(
        self,
        lead_id: int,
        customer_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get outreach history for a lead."""
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
        """Schedule an outreach message."""
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
        try:
            return await self.engine.send_outreach(lead_id, channel, message, customer_id)
        except Exception as e:
            raise ServiceUnavailableException(
                detail=f"Failed to send outreach message: {str(e)}"
            )

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
        try:
            return await self.engine.schedule_outreach(
                lead_id, channel, message, scheduled_time, customer_id
            )
        except Exception as e:
            raise ServiceUnavailableException(
                detail=f"Failed to schedule outreach: {str(e)}"
            ) 