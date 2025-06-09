# Import auth models last to avoid circular imports
from app.auth.models.auth import (LoginAttempt, MFASettings, PasswordReset,
                                  RefreshToken, UserSession)
from app.lead.models.lead import (ActivityType, Lead, LeadActivity, LeadScore,
                                  LeadSource, LeadStatus)
from app.outreach.models.outreach import (Outreach, OutreachLog,
                                          OutreachTemplate)
from app.project.models.project import (Project, ProjectAmenity,
                                        ProjectFeature, ProjectImage,
                                        ProjectStatus, ProjectType)
from app.scraping.models.scraping import ScrapingConfig
from app.shared.models.customer import Customer
from app.shared.models.interaction import InteractionLog
from app.shared.models.notification import Notification, NotificationPreference
from app.shared.models.user import User
from sqlalchemy.orm import Session
from app.lead.models.message import Message, MessageInteraction

# Re-export all models for backward compatibility
__all__ = [
    'User',
    'Customer',
    'Project',
    'ProjectFeature',
    'ProjectImage',
    'ProjectAmenity',
    'Lead',
    'Message',
    'MessageInteraction',
    'ActivityType',
    'InteractionLog',
    'Outreach',
    'OutreachTemplate',
    'OutreachLog',
    'Notification',
    'NotificationPreference',
    'LoginAttempt',
    'MFASettings',
    'PasswordReset',
    'UserSession',
    'ScrapingConfig'
] 