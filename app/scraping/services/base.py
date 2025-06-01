from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
import random
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.scraping.models.scraping import ScrapingConfig, ScrapingJob, ScrapingResult, ScrapingStatus
from app.shared.core.config import settings
import asyncio
import uuid
from fake_useragent import UserAgent
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
from ratelimit import limits, sleep_and_retry

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, db: Session, config: ScrapingConfig):
        self.db = db
        self.config = config
        self.proxies = settings.PROXY_LIST if hasattr(settings, 'PROXY_LIST') else []
        self.max_retries = config.max_retries
        self.retry_delay = config.scraping_delay
        self.ua = UserAgent()
        self.session = None
        self.job = None

    async def __aenter__(self):
        """Initialize aiohttp session."""
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()

    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy from the proxy list."""
        return random.choice(self.proxies) if self.proxies and self.config.proxy_enabled else None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @sleep_and_retry
    @limits(calls=10, period=60)
    async def make_request(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Make HTTP request with retry logic and rate limiting."""
        if not self.session:
            raise RuntimeError("Scraper session not initialized. Use 'async with' context manager.")

        proxy = self.get_random_proxy()
        proxy_url = f"http://{proxy}" if proxy else None

        try:
            async with self.session.get(
                url,
                headers=headers,
                proxy=proxy_url,
                timeout=self.config.scraping_delay
            ) as response:
                if response.status == 200:
                    return await response.text()
                logger.error(f"Request failed for {url}: {response.status}")
                return None
        except Exception as e:
            logger.error(f"Request error for {url}: {str(e)}")
            raise

    @abstractmethod
    async def scrape(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        """Main scraping method to be implemented by each scraper."""
        pass

    def create_job(self, source: str, location: str, property_type: str) -> ScrapingJob:
        """Create a new scraping job."""
        self.job = ScrapingJob(
            id=uuid.uuid4(),
            config_id=self.config.id,
            source=source,
            location=location,
            property_type=property_type,
            status=ScrapingStatus.PENDING
        )
        self.db.add(self.job)
        self.db.commit()
        return self.job

    def update_job_status(self, status: ScrapingStatus, items_scraped: int = 0, error_message: Optional[str] = None):
        """Update the status of the current scraping job."""
        if not self.job:
            raise RuntimeError("No active scraping job")

        self.job.status = status
        self.job.items_scraped = items_scraped
        self.job.error_message = error_message

        if status == ScrapingStatus.RUNNING:
            self.job.started_at = datetime.utcnow()
        elif status in [ScrapingStatus.COMPLETED, ScrapingStatus.FAILED]:
            self.job.completed_at = datetime.utcnow()

        self.db.commit()

    def save_results(self, results: List[Dict[str, Any]]) -> None:
        """Save scraped results to database."""
        if not self.job:
            raise RuntimeError("No active scraping job")

        for result_data in results:
            try:
                result = ScrapingResult(
                    id=uuid.uuid4(),
                    job_id=self.job.id,
                    title=result_data['title'],
                    description=result_data.get('description'),
                    price=result_data.get('price'),
                    location=result_data.get('location'),
                    property_type=result_data.get('property_type'),
                    bedrooms=result_data.get('bedrooms'),
                    bathrooms=result_data.get('bathrooms'),
                    area=result_data.get('area'),
                    images=result_data.get('images', []),
                    source_url=result_data.get('source_url'),
                    metadata=result_data.get('metadata', {})
                )
                self.db.add(result)
            except Exception as e:
                logger.error(f"Failed to save result: {str(e)}")
                continue

        try:
            self.db.commit()
            self.update_job_status(ScrapingStatus.COMPLETED, len(results))
        except Exception as e:
            logger.error(f"Failed to commit results: {str(e)}")
            self.db.rollback()
            self.update_job_status(ScrapingStatus.FAILED, 0, str(e))

    async def run(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        """Run the scraper with proper job tracking."""
        try:
            self.update_job_status(ScrapingStatus.RUNNING)
            results = await self.scrape(location, property_type)
            self.save_results(results)
            return results
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            self.update_job_status(ScrapingStatus.FAILED, 0, str(e))
            raise 