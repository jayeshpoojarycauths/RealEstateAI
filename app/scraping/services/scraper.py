from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.models.models import RealEstateProject, ScrapingConfig, Lead
from uuid import UUID
import time
import os
from datetime import datetime
import json
from abc import ABC, abstractmethod
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from app.shared.core.config import settings
import random
from ratelimit import limits, sleep_and_retry
from fake_useragent import UserAgent
import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from app.scraping.schemas.scraping import *
from app.scraping.services.base import BaseScraper
from app.scraping.services.ninety_nine_acres import NinetyNineAcresScraper
from app.scraping.services.facebook_marketplace import FacebookMarketplaceScraper

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, config: ScrapingConfig):
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

class MagicBricksScraper(BaseScraper):
    def scrape_properties(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        properties = []
        base_url = f"https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom=&proptype={property_type}&cityName={location}"
        
        for page in range(1, self.config.max_pages_per_source + 1):
            url = f"{base_url}&page={page}"
            response = self._make_request(url)
            if not response:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            property_cards = soup.find_all('div', class_='mb-srp__card')
            
            for card in property_cards:
                try:
                    property_data = {
                        'name': card.find('h2', class_='mb-srp__card--title').text.strip(),
                        'price': card.find('div', class_='mb-srp__card__price__amount').text.strip(),
                        'size': card.find('div', class_='mb-srp__card__desc__value').text.strip(),
                        'type': property_type,
                        'location': location,
                        'builder': card.find('div', class_='mb-srp__card__builder').text.strip(),
                        'completion_date': card.find('div', class_='mb-srp__card__completion').text.strip()
                    }
                    properties.append(self.parse_property(property_data))
                except Exception as e:
                    logger.error(f"Error parsing property card: {str(e)}")
                    continue

            time.sleep(self.config.scraping_delay)
        
        return properties

    def parse_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'name': property_data['name'],
            'price': property_data['price'],
            'size': property_data['size'],
            'type': property_data['type'],
            'builder': property_data['builder'],
            'location': property_data['location'],
            'completion_date': property_data['completion_date']
        }

class HousingScraper(BaseScraper):
    def scrape_properties(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        properties = []
        base_url = f"https://www.housing.com/in/buy/{location}/{property_type}"
        
        for page in range(1, self.config.max_pages_per_source + 1):
            url = f"{base_url}?page={page}"
            response = self._make_request(url)
            if not response:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            property_cards = soup.find_all('div', class_='project-card')
            
            for card in property_cards:
                try:
                    property_data = {
                        'name': card.find('h3', class_='project-name').text.strip(),
                        'price': card.find('div', class_='price').text.strip(),
                        'size': card.find('div', class_='size').text.strip(),
                        'type': property_type,
                        'location': location,
                        'builder': card.find('div', class_='builder').text.strip(),
                        'completion_date': card.find('div', class_='completion').text.strip()
                    }
                    properties.append(self.parse_property(property_data))
                except Exception as e:
                    logger.error(f"Error parsing property card: {str(e)}")
                    continue

            time.sleep(self.config.scraping_delay)
        
        return properties

    def parse_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'name': property_data['name'],
            'price': property_data['price'],
            'size': property_data['size'],
            'type': property_data['type'],
            'builder': property_data['builder'],
            'location': property_data['location'],
            'completion_date': property_data['completion_date']
        }

class PropTigerScraper(BaseScraper):
    def scrape_properties(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        properties = []
        base_url = f"https://www.proptiger.com/{location}/property-for-sale"
        
        for page in range(1, self.config.max_pages_per_source + 1):
            url = f"{base_url}?page={page}&propertyType={property_type}"
            response = self._make_request(url)
            if not response:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            property_cards = soup.find_all('div', class_='property-card')
            
            for card in property_cards:
                try:
                    property_data = {
                        'name': card.find('h3', class_='property-name').text.strip(),
                        'price': card.find('div', class_='price').text.strip(),
                        'size': card.find('div', class_='area').text.strip(),
                        'type': property_type,
                        'location': location,
                        'builder': card.find('div', class_='builder-name').text.strip(),
                        'completion_date': card.find('div', class_='possession').text.strip()
                    }
                    properties.append(self.parse_property(property_data))
                except Exception as e:
                    logger.error(f"Error parsing property card: {str(e)}")
                    continue

            time.sleep(self.config.scraping_delay)
        
        return properties

class CommonFloorScraper(BaseScraper):
    def scrape_properties(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        properties = []
        base_url = f"https://www.commonfloor.com/{location}/property-for-sale"
        
        for page in range(1, self.config.max_pages_per_source + 1):
            url = f"{base_url}?page={page}&propertyType={property_type}"
            response = self._make_request(url)
            if not response:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            property_cards = soup.find_all('div', class_='property-listing')
            
            for card in property_cards:
                try:
                    property_data = {
                        'name': card.find('h3', class_='property-title').text.strip(),
                        'price': card.find('div', class_='price-value').text.strip(),
                        'size': card.find('div', class_='area-value').text.strip(),
                        'type': property_type,
                        'location': location,
                        'builder': card.find('div', class_='builder-name').text.strip(),
                        'completion_date': card.find('div', class_='possession-date').text.strip()
                    }
                    properties.append(self.parse_property(property_data))
                except Exception as e:
                    logger.error(f"Error parsing property card: {str(e)}")
                    continue

            time.sleep(self.config.scraping_delay)
        
        return properties

    def parse_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'name': property_data['name'],
            'price': property_data['price'],
            'size': property_data['size'],
            'type': property_data['type'],
            'builder': property_data['builder'],
            'location': property_data['location'],
            'completion_date': property_data['completion_date']
        }

class ScraperService:
    def __init__(self, db: Session):
        self.db = db
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.scrapers = {
            'magicbricks': MagicBricksScraper,
            'housing': HousingScraper,
            'proptiger': PropTigerScraper,
            'commonfloor': CommonFloorScraper
        }

    def get_scraper(self, source: str, config: ScrapingConfig) -> BaseScraper:
        """Get the appropriate scraper for the source."""
        if source not in self.scrapers:
            raise ValueError(f"Unsupported source: {source}")
        
        return self.scrapers[source](config)

    async def scrape_all_sources_async(self, customer_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Asynchronously scrape properties from all enabled sources."""
        config = self.db.query(ScrapingConfig).filter(
            ScrapingConfig.customer_id == customer_id
        ).first()
        
        if not config:
            raise ValueError(f"No scraping configuration found for customer {customer_id}")
        
        tasks = []
        for source in config.enabled_sources:
            scraper = self.get_scraper(source, config)
            for location in config.locations:
                for property_type in config.property_types:
                    tasks.append(self._scrape_source_async(scraper, location, property_type))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self._process_async_results(results)

    async def _scrape_source_async(self, scraper: BaseScraper, location: str, property_type: str) -> Dict[str, Any]:
        """Asynchronously scrape a single source."""
        try:
            properties = await asyncio.to_thread(scraper.scrape_properties, location, property_type)
            return {
                'source': scraper.__class__.__name__,
                'location': location,
                'property_type': property_type,
                'properties': properties,
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error scraping {scraper.__class__.__name__}: {str(e)}")
            return {
                'source': scraper.__class__.__name__,
                'location': location,
                'property_type': property_type,
                'properties': [],
                'status': 'error',
                'error': str(e)
            }

    def _process_async_results(self, results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Process and organize async scraping results."""
        processed_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scraping task failed: {str(result)}")
                continue
            
            source = result['source']
            if source not in processed_results:
                processed_results[source] = []
            
            processed_results[source].extend(result['properties'])
        
        return processed_results

    def scrape_all_sources(self, customer_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape properties from all enabled sources."""
        return asyncio.run(self.scrape_all_sources_async(customer_id))

    def schedule_scraping(self, customer_id: str, interval_hours: int = 24):
        """Schedule automatic scraping."""
        job_id = f"scraping_{customer_id}"
        
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        self.scheduler.add_job(
            self.scrape_all_sources,
            CronTrigger(hour=f"*/{interval_hours}"),
            id=job_id,
            args=[customer_id]
        )

    def stop_scraping(self, customer_id: str):
        """Stop automatic scraping."""
        job_id = f"scraping_{customer_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id) 