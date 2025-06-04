import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.shared.db.session import SessionLocal
from app.scraping.services.scheduler import ScrapingScheduler
from app.scraping.models.scraping import ScrapingConfig

logger = logging.getLogger(__name__)

class ScrapingSchedulerTask:
    """Background task for managing the scraping scheduler."""

    def __init__(self):
        self.scheduler: Optional[ScrapingScheduler] = None
        self.db: Optional[Session] = None

    def start(self):
        """Start the scheduler task."""
        try:
            # Initialize database session
            self.db = SessionLocal()
            
            # Initialize scheduler
            self.scheduler = ScrapingScheduler(self.db)
            
            # Load and schedule existing configurations
            self._load_existing_configs()
            
            # Start the scheduler
            self.scheduler.start()
            
            logger.info("Scraping scheduler task started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scraping scheduler task: {str(e)}")
            self.shutdown()
            raise

    def shutdown(self):
        """Shutdown the scheduler task."""
        try:
            if self.scheduler:
                self.scheduler.shutdown()
                self.scheduler = None
            
            if self.db:
                self.db.close()
                self.db = None
            
            logger.info("Scraping scheduler task shutdown successfully")
            
        except Exception as e:
            logger.error(f"Error during scraping scheduler task shutdown: {str(e)}")

    def _load_existing_configs(self):
        """Load and schedule existing scraping configurations."""
        try:
            # Get all active configurations
            configs = self.db.query(ScrapingConfig).filter(
                ScrapingConfig.auto_scrape_enabled
            ).all()
            
            # Schedule each configuration
            for config in configs:
                self.scheduler.schedule_config(config)
            
            logger.info(f"Loaded {len(configs)} existing scraping configurations")
            
        except Exception as e:
            logger.error(f"Failed to load existing configurations: {str(e)}")
            raise

# Create global instance
scheduler_task = ScrapingSchedulerTask()

def start_scheduler():
    """Start the scraping scheduler task."""
    scheduler_task.start()

def shutdown_scheduler():
    """Shutdown the scraping scheduler task."""
    scheduler_task.shutdown() 