"""
This file ensures that all SQLAlchemy models are imported for metadata reflection and relationship resolution.
It is critical for migrations, string-based relationships, and enabling multi-tenancy via the Customer model.
"""

# Shared models
from app.shared.models.base import BaseModel
from app.shared.models.user import User
from app.shared.models.customer import Customer
from app.shared.models.notification import Notification, NotificationPreference
from app.shared.models.interaction import InteractionLog
from app.shared.models.audit import AuditLog

# Lead models
from app.lead.models.lead import Lead, LeadScore, LeadActivity

# Project models
from app.project.models.project import Project, ProjectFeature, ProjectImage, ProjectAmenity, RealEstateProject

# Outreach models
from app.outreach.models.outreach import Outreach, OutreachTemplate, OutreachLog, CommunicationPreference, OutreachCampaign

# Scraping models
from app.scraping.models.scraping import ScrapingConfig, ScrapingJob, ScrapingResult

# Auth models
from app.auth.models.auth import MFASettings, UserSession, LoginAttempt, PasswordReset, RefreshToken 