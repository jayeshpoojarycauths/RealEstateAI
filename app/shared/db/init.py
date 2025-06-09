import logging

from app.shared.db.init_db import init_db
from app.shared.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.shared.core.logging import logger
from sqlalchemy.orm import Session
from app.shared.core.logging import logger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init() -> None:
    db = SessionLocal()
    init_db(db)

def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")

if __name__ == "__main__":
    main() 