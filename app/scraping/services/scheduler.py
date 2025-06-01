from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from app.scraping.services.scraper import ScraperService
from app.scraping.models.scraping import ScrapingConfig, ScrapingStatus
from app.shared.core.config import settings

logger = logging.getLogger(__name__)

class ScrapingScheduler:
    """Service for scheduling automated scraping jobs."""

    def __init__(self, db: Session):
        self.db = db
        self.scraper_service = ScraperService(db)
        
        # Configure job stores
        jobstores = {
            'default': SQLAlchemyJobStore(url=settings.SQLALCHEMY_DATABASE_URI)
        }
        
        # Configure executors
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        
        # Configure job defaults
        job_defaults = {
            'coalesce': False,
            'max_instances': 1
        }
        
        # Initialize scheduler
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scraping scheduler started")

    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scraping scheduler shutdown")

    def schedule_config(self, config: ScrapingConfig):
        """Schedule scraping jobs for a configuration."""
        if not config.auto_scrape_enabled:
            return

        job_id = f"scraping_config_{config.id}"
        
        # Remove existing job if it exists
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        # Calculate cron expression based on interval
        cron_expression = self._get_cron_expression(config.auto_scrape_interval)
        
        # Add new job
        self.scheduler.add_job(
            self._run_config_jobs,
            CronTrigger.from_crontab(cron_expression),
            id=job_id,
            args=[config.id],
            replace_existing=True
        )
        
        logger.info(f"Scheduled scraping jobs for config {config.id}")

    def unschedule_config(self, config_id: str):
        """Remove scheduled jobs for a configuration."""
        job_id = f"scraping_config_{config_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed scheduled jobs for config {config_id}")

    async def _run_config_jobs(self, config_id: str):
        """Run all scraping jobs for a configuration."""
        try:
            config = self.db.query(ScrapingConfig).filter(
                ScrapingConfig.id == config_id
            ).first()
            
            if not config or not config.auto_scrape_enabled:
                return

            # Update last run time
            config.last_run_at = datetime.utcnow()
            self.db.commit()

            # Run jobs for each enabled source and location
            for source in config.enabled_sources:
                for location in config.locations:
                    for property_type in config.property_types:
                        try:
                            await self.scraper_service.run_scraping_job(
                                config.id,
                                source,
                                location,
                                property_type
                            )
                        except Exception as e:
                            logger.error(f"Failed to run scheduled job: {str(e)}")
                            continue

        except Exception as e:
            logger.error(f"Error running scheduled jobs for config {config_id}: {str(e)}")

    def _get_cron_expression(self, interval_hours: int) -> str:
        """Convert interval hours to cron expression."""
        if interval_hours < 1:
            interval_hours = 1
        elif interval_hours > 24:
            interval_hours = 24

        return f"0 */{interval_hours} * * *"  # Run every X hours

    def get_scheduled_jobs(self) -> Dict[str, Any]:
        """Get information about all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return {
            'total_jobs': len(jobs),
            'jobs': jobs
        } 