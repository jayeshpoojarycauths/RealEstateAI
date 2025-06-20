from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.shared.core.config import settings
from app.shared.models.base import Base
from app.shared.models.customer import Customer
from app.shared.models.user import Permission, Role, User
from sqlalchemy.orm import Session
from app.shared.models.user import User
from sqlalchemy.orm import Session
from app.shared.models.user import User

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    **settings.get_database_engine_options
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Import all models here for Alembic
__all__ = [
    "Base",
    "User",
    "Role",
    "Permission",
    "Customer"
] 