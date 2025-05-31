from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.shared.core.config import settings

engine = create_engine(
    settings.get_database_url,
    **settings.get_database_engine_options
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 