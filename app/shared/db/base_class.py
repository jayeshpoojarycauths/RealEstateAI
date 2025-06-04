from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    """Base class for all models with common fields."""
    __abstract__ = True

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self):
        """Soft delete the model."""
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore a soft-deleted model."""
        self.deleted_at = None

__all__ = ['Base', 'BaseModel'] 