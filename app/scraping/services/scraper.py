import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type

import aiohttp
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from ratelimit import limits, sleep_and_retry
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

from app.scraping.models.scraping import (ScrapingConfig, ScrapingJob,
                                          ScrapingResult, ScrapingSource,
                                          ScrapingStatus)
from app.scraping.schemas.scraping import *
from app.scraping.services.base import BaseScraper
from app.scraping.services.ninety_nine_acres import NinetyNineAcresScraper
from app.shared.core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, db: Session, config: ScrapingConfig):
        self.db = db
        self.config = config
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        if config.proxy_enabled and config.proxy_url:
            self.session.proxies = {
                'http': config.proxy_url,
                'https': config.proxy_url
            }
        
        self.rate_limit = config.rate_limit or 10  # requests per minute
        self.retry_count = config.retry_count or 3
        self.timeout = config.timeout or 30
        self.source = None

    @abstractmethod
    def scrape_properties(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        """Scrape properties from the source."""
        pass

    @abstractmethod
    def parse_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse property data into a standardized format."""
        pass

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @sleep_and_retry
    @limits(calls=10, period=60)
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and rate limiting."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"Successfully fetched {url}")
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            raise

    async def _make_async_request(self, url: str) -> Optional[str]:
        """Make asynchronous HTTP request."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status == 200:
                        return await response.text()
                    logger.error(f"Async request failed for {url}: {response.status}")
                    return None
            except Exception as e:
                logger.error(f"Async request error for {url}: {str(e)}")
                return None

    def make_request(self, url: str) -> Optional[str]:
        """Make HTTP request and return the response text."""
        response = self._make_request(url)
        return response.text if response else None

class MagicBricksScraper(BaseScraper):
    def __init__(self, db: Session, config: ScrapingConfig):
        super().__init__(db, config)
        self.source = ScrapingSource.MAGICBRICKS

    async def scrape(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        properties = []
        base_url = f"https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom=&proptype={property_type}&cityName={location}"
        for page in range(1, self.config.max_pages_per_source + 1):
            url = f"{base_url}&page={page}"
            html = await self.make_request(url)
            if not html:
                continue
            soup = BeautifulSoup(html, 'html.parser')
            property_cards = soup.find_all('div', class_='mb-srp__card')
            for card in property_cards:
                try:
                    property_data = {
                        'title': card.find('h2', class_='mb-srp__card--title').text.strip(),
                        'price': card.find('div', class_='mb-srp__card__price__amount').text.strip(),
                        'size': card.find('div', class_='mb-srp__card__desc__value').text.strip(),
                        'property_type': property_type,
                        'location': location,
                        'builder': card.find('div', class_='mb-srp__card__builder').text.strip(),
                        'completion_date': card.find('div', class_='mb-srp__card__completion').text.strip()
                    }
                    properties.append(property_data)
                except Exception as e:
                    logger.error(f"Error parsing property card: {str(e)}")
                    continue
            await asyncio.sleep(self.config.scraping_delay)
        return properties

    def parse_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'name': property_data['title'],
            'price': property_data['price'],
            'size': property_data['size'],
            'type': property_data['property_type'],
            'builder': property_data['builder'],
            'location': property_data['location'],
            'completion_date': property_data['completion_date']
        }

class HousingScraper(BaseScraper):
    def __init__(self, db: Session, config: ScrapingConfig):
        super().__init__(db, config)
        self.source = ScrapingSource.HOUSING

    async def scrape(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        properties = []
        base_url = f"https://www.housing.com/in/buy/{location}/{property_type}"
        for page in range(1, self.config.max_pages_per_source + 1):
            url = f"{base_url}?page={page}"
            html = await self.make_request(url)
            if not html:
                continue
            soup = BeautifulSoup(html, 'html.parser')
            property_cards = soup.find_all('div', class_='project-card')
            for card in property_cards:
                try:
                    property_data = {
                        'title': card.find('h3', class_='project-name').text.strip(),
                        'price': card.find('div', class_='price').text.strip(),
                        'size': card.find('div', class_='size').text.strip(),
                        'property_type': property_type,
                        'location': location,
                        'builder': card.find('div', class_='builder').text.strip(),
                        'completion_date': card.find('div', class_='completion').text.strip()
                    }
                    properties.append(property_data)
                except Exception as e:
                    logger.error(f"Error parsing property card: {str(e)}")
                    continue
            await asyncio.sleep(self.config.scraping_delay)
        return properties

    def parse_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'name': property_data['title'],
            'price': property_data['price'],
            'size': property_data['size'],
            'type': property_data['property_type'],
            'builder': property_data['builder'],
            'location': property_data['location'],
            'completion_date': property_data['completion_date']
        }

class PropTigerScraper(BaseScraper):
    def __init__(self, db: Session, config: ScrapingConfig):
        super().__init__(db, config)
        self.source = ScrapingSource.PROPTIGER

    async def scrape(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        properties = []
        base_url = f"https://www.proptiger.com/{location}/property-for-sale"
        for page in range(1, self.config.max_pages_per_source + 1):
            url = f"{base_url}?page={page}&propertyType={property_type}"
            html = await self.make_request(url)
            if not html:
                continue
            soup = BeautifulSoup(html, 'html.parser')
            property_cards = soup.find_all('div', class_='property-card')
            for card in property_cards:
                try:
                    property_data = {
                        'title': card.find('h2', class_='property-title').text.strip(),
                        'price': card.find('div', class_='property-price').text.strip(),
                        'size': card.find('div', class_='property-size').text.strip(),
                        'property_type': property_type,
                        'location': location,
                        'builder': card.find('div', class_='property-builder').text.strip(),
                        'completion_date': card.find('div', class_='property-completion').text.strip()
                    }
                    properties.append(property_data)
                except Exception as e:
                    logger.error(f"Error parsing property card: {str(e)}")
                    continue
            await asyncio.sleep(self.config.scraping_delay)
        return properties

    def parse_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'name': property_data['title'],
            'price': property_data['price'],
            'size': property_data['size'],
            'type': property_data['property_type'],
            'builder': property_data['builder'],
            'location': property_data['location'],
            'completion_date': property_data['completion_date']
        }

class CommonFloorScraper(BaseScraper):
    def __init__(self, db: Session, config: ScrapingConfig):
        super().__init__(db, config)
        self.source = ScrapingSource.COMMONFLOOR

    async def scrape(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        properties = []
        base_url = f"https://www.commonfloor.com/listing-search?city={location}&propertyType={property_type}"
        for page in range(1, self.config.max_pages_per_source + 1):
            url = f"{base_url}&page={page}"
            html = await self.make_request(url)
            if not html:
                continue
            soup = BeautifulSoup(html, 'html.parser')
            property_cards = soup.find_all('div', class_='listing-card')
            for card in property_cards:
                try:
                    property_data = {
                        'title': card.find('h2', class_='listing-title').text.strip(),
                        'price': card.find('div', class_='listing-price').text.strip(),
                        'size': card.find('div', class_='listing-size').text.strip(),
                        'property_type': property_type,
                        'location': location,
                        'builder': card.find('div', class_='listing-builder').text.strip(),
                        'completion_date': card.find('div', class_='listing-completion').text.strip()
                    }
                    properties.append(property_data)
                except Exception as e:
                    logger.error(f"Error parsing property card: {str(e)}")
                    continue
            await asyncio.sleep(self.config.scraping_delay)
        return properties

    def parse_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'name': property_data['title'],
            'price': property_data['price'],
            'size': property_data['size'],
            'type': property_data['property_type'],
            'builder': property_data['builder'],
            'location': property_data['location'],
            'completion_date': property_data['completion_date']
        }

class ScraperFactory:
    """Factory class for creating scraper instances."""
    
    @staticmethod
    def create_scraper(source: str, db: Session, config: ScrapingConfig) -> BaseScraper:
        """Create a scraper instance based on the source."""
        if source.lower() == "99acres":
            return NinetyNineAcresScraper(db, config)
        elif source.lower() == "magicbricks":
            return MagicBricksScraper(db, config)
        else:
            raise ValueError(f"Unsupported scraping source: {source}")

class ScrapingService:
    """Service for managing property scraping operations."""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def scrape_properties(
        self,
        source: str,
        location: str,
        max_pages: int = 1,
        config: Optional[ScrapingConfig] = None
    ) -> List[ScrapingResult]:
        """Scrape properties from the specified source."""
        try:
            scraper = ScraperFactory.create_scraper(source, self.db, config or ScrapingConfig())
            results = await scraper.scrape_properties(location, max_pages)
            return results
        except Exception as e:
            logger.error(f"Error scraping properties: {str(e)}")
            raise

class ScraperService:
    """Service for managing property scrapers."""

    def __init__(self, db: Session):
        self.db = db
        self.scrapers: Dict[ScrapingSource, Type[BaseScraper]] = {
            ScrapingSource.MAGICBRICKS: MagicBricksScraper,
            # Add other scrapers here as they are implemented
        }
        self._scheduler = None  # Lazy initialization

    @property
    def scheduler(self):
        """Lazy initialization of scheduler."""
        if self._scheduler is None:
            from app.scraping.services.scheduler import ScrapingScheduler
from fastapi import Request
from sqlalchemy.orm import Session
from app.shared.models.user import User
from datetime import datetime
from typing import Dict
from typing import Any
from app.shared.core.logging import logger
from app.shared.core.exceptions import ValidationError
from datetime import timedelta
from fastapi import Request
from sqlalchemy.orm import Session
from app.shared.models.user import User
from datetime import datetime
from typing import Dict
from typing import Any
from app.shared.core.logging import logger
from app.shared.core.exceptions import ValidationError
from datetime import timedelta
            self._scheduler = ScrapingScheduler(self.db)
        return self._scheduler

    async def create_config(self, config_data: Dict[str, Any], customer_id: str) -> ScrapingConfig:
        """Create a new scraping configuration."""
        config = ScrapingConfig(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            enabled_sources=config_data.get('enabled_sources', []),
            locations=config_data.get('locations', []),
            property_types=config_data.get('property_types', []),
            price_range_min=config_data.get('price_range_min'),
            price_range_max=config_data.get('price_range_max'),
            max_pages_per_source=config_data.get('max_pages_per_source', 10),
            scraping_delay=config_data.get('scraping_delay', 5),
            max_retries=config_data.get('max_retries', 3),
            proxy_enabled=config_data.get('proxy_enabled', False),
            proxy_url=config_data.get('proxy_url'),
            user_agent=config_data.get('user_agent'),
            auto_scrape_enabled=config_data.get('auto_scrape_enabled', False),
            auto_scrape_interval=config_data.get('auto_scrape_interval', 24)
        )
        
        self.db.add(config)
        self.db.commit()
        
        # Schedule if auto-scrape is enabled
        if config.auto_scrape_enabled:
            self.scheduler.schedule_config(config)
        
        return config

    async def get_config(self, config_id: str, customer_id: str) -> ScrapingConfig:
        """Get a scraping configuration."""
        config = self.db.query(ScrapingConfig).filter(
            ScrapingConfig.id == config_id,
            ScrapingConfig.customer_id == customer_id
        ).first()
        
        if not config:
            raise NotFoundError(f"Scraping configuration not found: {config_id}")
        
        return config

    async def list_configs(self, customer_id: str, skip: int = 0, limit: int = 100) -> List[ScrapingConfig]:
        """List scraping configurations for a customer."""
        return self.db.query(ScrapingConfig).filter(
            ScrapingConfig.customer_id == customer_id
        ).offset(skip).limit(limit).all()

    async def update_config(self, config_id: str, config_data: Dict[str, Any], customer_id: str) -> ScrapingConfig:
        """Update a scraping configuration."""
        config = await self.get_config(config_id, customer_id)
        
        # Update fields
        for key, value in config_data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.db.commit()
        
        # Update scheduler
        if config.auto_scrape_enabled:
            self.scheduler.schedule_config(config)
        else:
            self.scheduler.unschedule_config(config.id)
        
        return config

    async def delete_config(self, config_id: str, customer_id: str):
        """Delete a scraping configuration."""
        config = await self.get_config(config_id, customer_id)
        
        # Remove from scheduler
        self.scheduler.unschedule_config(config.id)
        
        # Delete from database
        self.db.delete(config)
        self.db.commit()

    async def run_scraping_job(self, config_id: str, source: ScrapingSource, location: str, property_type: str) -> ScrapingJob:
        """Run a scraping job for a specific source and location."""
        # Get scraping configuration
        config = self.db.query(ScrapingConfig).filter(ScrapingConfig.id == config_id).first()
        if not config:
            raise NotFoundError(f"Scraping configuration not found: {config_id}")

        # Create scraping job
        job = ScrapingJob(
            id=str(uuid.uuid4()),
            config_id=config_id,
            source=source,
            location=location,
            property_type=property_type,
            status=ScrapingStatus.PENDING
        )
        self.db.add(job)
        self.db.commit()

        try:
            # Get appropriate scraper
            scraper_class = self.scrapers.get(source)
            if not scraper_class:
                raise ValidationError(f"No scraper implementation for source: {source}")

            # Use async context manager and call scrape()
            async with scraper_class(self.db, config) as scraper:
                results = await scraper.scrape(location, property_type)

            # Update job status
            job.status = ScrapingStatus.COMPLETED
            job.items_scraped = len(results)
            job.completed_at = datetime.utcnow()
            self.db.commit()

            return job

        except Exception as e:
            logger.error(f"Scraping job failed: {str(e)}")
            job.status = ScrapingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    async def run_scheduled_jobs(self) -> None:
        """Run all scheduled scraping jobs."""
        # Get all active configurations
        configs = self.db.query(ScrapingConfig).filter(
            ScrapingConfig.auto_scrape_enabled
        ).all()

        for config in configs:
            # Check if it's time to run
            if not self._should_run_scheduled_job(config):
                continue
            
            # Run jobs for each enabled source and location
            for source in config.enabled_sources:
                for location in config.locations:
                    for property_type in config.property_types:
                        try:
                            await self.run_scraping_job(
                                config.id,
                                source,
                                location,
                                property_type
                            )
                        except Exception as e:
                            logger.error(f"Failed to run scheduled job: {str(e)}")
                            continue

    def _should_run_scheduled_job(self, config: ScrapingConfig) -> bool:
        """Check if a scheduled job should run based on its interval."""
        if not config.last_run_at:
            return True

        interval = timedelta(hours=config.auto_scrape_interval)
        return datetime.utcnow() - config.last_run_at >= interval

    def get_job_status(self, job_id: str) -> ScrapingJob:
        """Get the status of a scraping job."""
        job = self.db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
        if not job:
            raise NotFoundError(f"Scraping job not found: {job_id}")
        return job

    def list_jobs(
        self,
        config_id: Optional[str] = None,
        source: Optional[ScrapingSource] = None,
        status: Optional[ScrapingStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ScrapingJob]:
        """List scraping jobs with optional filters."""
        query = self.db.query(ScrapingJob)

        if config_id:
            query = query.filter(ScrapingJob.config_id == config_id)
        if source:
            query = query.filter(ScrapingJob.source == source)
        if status:
            query = query.filter(ScrapingJob.status == status)
        if start_date:
            query = query.filter(ScrapingJob.created_at >= start_date)
        if end_date:
            query = query.filter(ScrapingJob.created_at <= end_date)

        return query.order_by(ScrapingJob.created_at.desc()).offset(skip).limit(limit).all()

    def get_job_results(
        self,
        job_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ScrapingResult]:
        """Get results for a specific scraping job."""
        return self.db.query(ScrapingResult).filter(
            ScrapingResult.job_id == job_id
        ).offset(skip).limit(limit).all()

    def get_scraping_stats(self, config_id: str) -> Dict[str, Any]:
        """Get scraping statistics for a configuration."""
        # Get all jobs for this configuration
        jobs = self.db.query(ScrapingJob).filter(
            ScrapingJob.config_id == config_id
        ).all()

        total_jobs = len(jobs)
        completed_jobs = sum(1 for job in jobs if job.status == ScrapingStatus.COMPLETED)
        failed_jobs = sum(1 for job in jobs if job.status == ScrapingStatus.FAILED)
        total_items = sum(job.items_scraped for job in jobs)

        # Calculate success rate
        success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0

        # Get source distribution
        source_distribution = {}
        for job in jobs:
            source = job.source.value
            source_distribution[source] = source_distribution.get(source, 0) + 1

        return {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'total_items': total_items,
            'success_rate': success_rate,
            'source_distribution': source_distribution
        }

    def get_active_configs(self) -> List[ScrapingConfig]:
        """Get all active scraping configurations."""
        return self.db.query(ScrapingConfig).filter(
            ScrapingConfig.auto_scrape_enabled
        ).all()

    def get_configs_for_scheduler(self) -> List[ScrapingConfig]:
        """Get configurations for scheduler."""
        return self.db.query(ScrapingConfig).filter(
            ScrapingConfig.auto_scrape_enabled
        ).all() 