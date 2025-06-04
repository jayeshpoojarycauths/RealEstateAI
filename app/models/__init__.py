from app.project.models.project import (
    Project,
    ProjectFeature,
    ProjectImage,
    ProjectAmenity,
    RealEstateProject,
    ProjectType,
    ProjectStatus
)
from app.lead.models.lead import (
    Lead,
    LeadActivity,
    LeadScore,
    LeadStatus,
    LeadSource,
    ActivityType
)
from app.shared.models.user import User
from app.shared.models.customer import Customer
from app.shared.models.interaction import InteractionLog
from app.outreach.models.outreach import Outreach, OutreachTemplate, OutreachLog
from app.shared.models.notification import Notification, NotificationPreference
from app.scraping.models.scraping import ScrapingConfig

# Import auth models last to avoid circular imports
from app.auth.models.auth import (
    RefreshToken,
    LoginAttempt,
    MFASettings,
    PasswordReset,
    UserSession
)

# Re-export all models for backward compatibility
__all__ = [
    'Project',
    'ProjectFeature',
    'ProjectImage',
    'ProjectAmenity',
    'RealEstateProject',
    'ProjectType',
    'ProjectStatus',
    'Lead',
    'LeadActivity',
    'LeadScore',
    'LeadStatus',
    'LeadSource',
    'ActivityType',
    'User',
    'Customer',
    'InteractionLog',
    'Outreach',
    'OutreachTemplate',
    'OutreachLog',
    'Notification',
    'NotificationPreference',
    'RefreshToken',
    'LoginAttempt',
    'MFASettings',
    'PasswordReset',
    'UserSession',
    'ScrapingConfig'
] 