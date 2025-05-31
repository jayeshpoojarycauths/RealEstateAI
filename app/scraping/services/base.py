from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
import random
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Customer, RealEstateProject, Lead, ScrapingConfig
from app.shared.core.config import settings
import asyncio
import uuid

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, db: Session, customer: Customer):
        self.db = db
        self.customer = customer
        self.proxies = settings.PROXY_LIST
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    @abstractmethod
    async def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method to be implemented by each scraper"""
        pass

    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy from the proxy list"""
        return random.choice(self.proxies) if self.proxies else None

    async def make_request(self, url: str, headers: Dict[str, str] = None) -> Any:
        """Make HTTP request with retry logic and proxy rotation"""
        for attempt in range(self.max_retries):
            try:
                proxy = self.get_random_proxy()
                # Implementation will be in child classes
                return await self._make_request_impl(url, headers, proxy)
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

    @abstractmethod
    async def _make_request_impl(self, url: str, headers: Dict[str, str], proxy: Optional[str]) -> Any:
        """Implementation of HTTP request to be defined by each scraper"""
        pass

    def save_projects(self, projects: List[Dict[str, Any]]) -> None:
        """Save scraped projects to database"""
        for project_data in projects:
            try:
                project = RealEstateProject(
                    customer_id=self.customer.id,
                    title=project_data['title'],
                    description=project_data.get('description', ''),
                    price=project_data['price'],
                    location=project_data['location'],
                    property_type=project_data.get('property_type'),
                    bedrooms=project_data.get('bedrooms'),
                    bathrooms=project_data.get('bathrooms'),
                    area=project_data.get('area'),
                    images=project_data.get('images', []),
                    source=project_data['source'],
                    source_url=project_data['source_url'],
                    metadata=project_data.get('metadata', {}),
                    created_at=datetime.utcnow()
                )
                self.db.add(project)
            except Exception as e:
                logger.error(f"Failed to save project: {str(e)}")
                continue

        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to commit projects: {str(e)}")
            self.db.rollback()

    def save_leads(self, leads: List[Dict[str, Any]]) -> None:
        """Save scraped leads to database"""
        for lead_data in leads:
            try:
                lead = Lead(
                    customer_id=self.customer.id,
                    name=lead_data['name'],
                    email=lead_data.get('email'),
                    phone=lead_data.get('phone'),
                    source=lead_data['source'],
                    notes=lead_data.get('notes', ''),
                    created_at=datetime.utcnow()
                )
                self.db.add(lead)
            except Exception as e:
                logger.error(f"Failed to save lead: {str(e)}")
                continue

        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to commit leads: {str(e)}")
            self.db.rollback() 