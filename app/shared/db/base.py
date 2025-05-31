from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.shared.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.get_database_url,
    **settings.get_database_engine_options
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Import all models here for Alembic
from app.models.models import (
    User,
    Customer,
    Lead,
    Project,
    ProjectLead,
    CommunicationPreferences,
    AuditLog,
    OutreachLog,
    InteractionLog
) 