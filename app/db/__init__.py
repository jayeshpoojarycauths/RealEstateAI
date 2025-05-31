from app.shared.db.session import SessionLocal, engine
from app.shared.db.base import Base

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 