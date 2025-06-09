from app.shared.db.base import Base
from app.shared.db.session import SessionLocal, engine
from sqlalchemy.orm import Session
from app.shared.db.session import get_db
from sqlalchemy.orm import Session
from app.shared.db.session import get_db

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 