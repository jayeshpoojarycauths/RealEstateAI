from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import random
from app.models.models import Lead, Outreach, CommunicationPreferences

class OutreachResult:
    def __init__(self, status: str, response_time: Optional[float] = None):
        self.status = status
        self.response_time = response_time

class MockOutreachEngine:
    def __init__(self, preferences: CommunicationPreferences):
        self.preferences = preferences
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

    def generate_message(self, lead: Lead) -> str:
        """Generate a message based on the lead and channel."""
        channel = self.preferences.default_channel
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

    def send(self, outreach: Outreach) -> OutreachResult:
        """Simulate sending an outreach message."""
        # Simulate network delay
        delay = random.uniform(0.5, 2.0)
        
        # Simulate success/failure
        success_rate = {
            'email': 0.95,
            'sms': 0.90,
            'whatsapp': 0.85,
            'telegram': 0.80
        }.get(outreach.channel, 0.90)

        if random.random() < success_rate:
            # Simulate response time
            response_time = random.uniform(1.0, 24.0)  # 1-24 hours
            return OutreachResult(
                status='delivered',
                response_time=response_time
            )
        else:
            return OutreachResult(
                status='failed',
                response_time=None
            ) 