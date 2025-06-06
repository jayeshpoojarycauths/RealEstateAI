from typing import List, Dict, Any
import asyncio
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from app.shared.models.customer import Customer
from app.scraping.models.scraping import ScrapingConfig
from app.lead.models.lead import Lead
from app.shared.core.config import settings
from app.scraping.services.base import BaseScraper
from app.scraping.services.ninety_nine_acres import NinetyNineAcresScraper
from app.scraping.services.facebook_marketplace import FacebookMarketplaceScraper

logger = logging.getLogger(__name__)

class ScraperScheduler:
    def __init__(self, db: Session):
        self.db = db
        self.scrapers: Dict[str, BaseScraper] = {}
        self.running = False
        self.last_run: Dict[str, datetime] = {}
        self.scrape_interval = timedelta(hours=settings.SCRAPE_INTERVAL_HOURS)
        self._scraper_service = None  # Lazy initialization

    @property
    def scraper_service(self):
        """Lazy initialization of scraper service."""
        if self._scraper_service is None:
            from app.scraping.services.scraper import ScraperService
            self._scraper_service = ScraperService(self.db)
        return self._scraper_service

    async def start(self):
        """Start the scraper scheduler"""
        self.running = True
        while self.running:
            try:
                await self._run_scheduled_scrapers()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scraper scheduler: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    def stop(self):
        """Stop the scraper scheduler"""
        self.running = False

    async def _run_scheduled_scrapers(self):
        """Run scrapers that are due for execution"""
        current_time = datetime.utcnow()
        
        # Get all active customers
        customers = self.db.query(Customer).all()
        
        for customer in customers:
            # Initialize scrapers for customer if not exists
            if customer.id not in self.scrapers:
                self.scrapers[customer.id] = {
                    '99acres': NinetyNineAcresScraper(self.db, customer),
                    'facebook': FacebookMarketplaceScraper(self.db, customer)
                }
                self.last_run[customer.id] = {}
            
            # Check each scraper
            for scraper_name, scraper in self.scrapers[customer.id].items():
                last_run = self.last_run[customer.id].get(scraper_name)
                
                if not last_run or (current_time - last_run) >= self.scrape_interval:
                    try:
                        logger.info(f"Running {scraper_name} scraper for customer {customer.id}")
                        projects = await scraper.scrape()
                        
                        # Save scraped data
                        scraper.save_projects(projects)
                        
                        # Update last run time
                        self.last_run[customer.id][scraper_name] = current_time
                        
                        logger.info(f"Successfully scraped {len(projects)} projects from {scraper_name}")
                    except Exception as e:
                        logger.error(f"Error running {scraper_name} scraper: {str(e)}")
                        # Don't update last_run time on error

    async def run_scraper_now(self, customer_id: str, scraper_name: str) -> List[Dict[str, Any]]:
        """Run a specific scraper immediately"""
        if customer_id not in self.scrapers:
            customer = self.db.query(Customer).get(customer_id)
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")
            
            self.scrapers[customer_id] = {
                '99acres': NinetyNineAcresScraper(self.db, customer),
                'facebook': FacebookMarketplaceScraper(self.db, customer)
            }
        
        if scraper_name not in self.scrapers[customer_id]:
            raise ValueError(f"Scraper {scraper_name} not found")
        
        scraper = self.scrapers[customer_id][scraper_name]
        projects = await scraper.scrape()
        scraper.save_projects(projects)
        
        return projects 