"""
Shared models package initialization.
"""

from app.shared.db.base_class import Base  # Import Base first

# Import models in dependency order
from app.auth.models.auth import UserSession  # Import UserSession first
from app.lead.models.lead import Lead  # Import Lead first
from .interaction import InteractionLog, CallInteraction, MessageInteraction  # Import after Lead
from .customer import Customer  # Import Customer after Lead
from app.project.models.project import Project, ProjectFeature, ProjectImage, ProjectAmenity, ProjectType, ProjectStatus  # Import Project models
from .user import User  # Import User after Customer
from .notification import Notification, NotificationPreference
from .audit import AuditLog  # Import AuditLog after User since it depends on User

# Import outreach models
from app.outreach.models.outreach import Outreach

# Import scraping models after all shared models are imported
from app.scraping.models.scraping import ScrapingConfig

# Ensure all models are imported before configuring mappers
__all__ = [
    "AuditLog",
    "Base",
    "CallInteraction",
    "Customer",
    "InteractionLog",
    "Lead",
    "MessageInteraction",
    "Notification",
    "NotificationPreference",
    "Project",
    "ProjectFeature",
    "ProjectImage",
    "ProjectAmenity",
    "ProjectType",
    "ProjectStatus",
    "User",
    "UserSession",
    "Outreach",
    "ScrapingConfig"
]

# Configure mappers after all models are imported
from sqlalchemy.orm import configure_mappers
configure_mappers()
