from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import ScrapingConfig, Customer
from app.shared.core.config import settings
import logging
from app.services.scraped_lead import save_scraped_leads
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_listings(
        self,
        location: str,
        property_type: str = "residential",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        max_pages: int = 5
    ) -> List[Dict]:
        """
        Base method for scraping property listings.
        Should be implemented by child classes.
        """
        raise NotImplementedError("Child classes must implement scrape_listings method")

class UserScraper(BaseScraper):
    async def scrape_listings(self, location: str = "", max_pages: int = 5) -> List[Dict]:
        users = []
        base_url = "https://www.99acres.com"
        search_url = f"{base_url}/property-for-sale-in-{location.lower()}-ffid"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            for page in range(1, max_pages + 1):
                url = f"{search_url}?page={page}"
                async with session.get(url) as response:
                    if response.status != 200:
                        continue
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    # Each property card
                    for card in soup.select(".srpTuple__tupleDetails"):
                        # Agent/owner name
                        name_tag = card.select_one(".srpTuple__postedBy")
                        name = name_tag.text.strip() if name_tag else "Unknown"
                        # Phone number (sometimes obfuscated or loaded via JS, so may not always be available)
                        phone_tag = card.select_one(".srpTuple__contactBtn")
                        phone = phone_tag['data-phone'] if phone_tag and phone_tag.has_attr('data-phone') else "Not available"
                        users.append({
                            "name": name,
                            "email": "",
                            "phone": phone,
                            "location": location
                        })
        return users

class LocationScraper(BaseScraper):
    async def scrape_listings(self, max_pages: int = 5) -> List[Dict]:
        # Simulate scraping multiple locations
        locations = []
        sample_locations = ["Mumbai", "Bangalore", "Delhi", "Chennai", "Hyderabad"]
        trends = ["hot", "rising", "stable", "cooling", "declining"]
        for i in range(min(max_pages, len(sample_locations))):
            locations.append({
                "location": sample_locations[i],
                "trend": trends[i % len(trends)]
            })
        return locations

class ScraperService:
    def __init__(self, db: Session):
        self.db = db
    
    async def scrape_properties(
        self,
        customer_id: int,
        location: str,
        property_type: str = "residential",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        max_pages: int = 5
    ) -> List[Dict]:
        """
        Scrape properties from multiple sources.
        
        Args:
            customer_id: ID of the customer to scrape for
            location: Location to search in
            property_type: Type of property (residential/commercial)
            min_price: Minimum price filter
            max_price: Maximum price filter
            max_pages: Maximum number of pages to scrape per source
            
        Returns:
            List of property listings
        """
        all_listings = []
        
        # Get customer's scraping configuration
        config = self.db.query(ScrapingConfig).filter(
            ScrapingConfig.customer_id == customer_id
        ).first()
        
        if not config:
            logger.warning(f"No scraping configuration found for customer {customer_id}")
            return all_listings
        
        # Scrape from MagicBricks if enabled
        if config.magicbricks_enabled:
            async with MagicBricksScraper() as scraper:
                listings = await scraper.scrape_listings(
                    location=location,
                    property_type=property_type,
                    min_price=min_price,
                    max_price=max_price,
                    max_pages=max_pages
                )
                all_listings.extend(listings)
                # Save scraped leads
                save_scraped_leads(self.db, customer_id, lead_type="property", source="magicbricks", leads=listings)
        
        # Scrape from 99acres if enabled
        if config.ninety_nine_acres_enabled:
            async with NinetyNineAcresScraper() as scraper:
                listings = await scraper.scrape_listings(
                    location=location,
                    property_type=property_type,
                    min_price=min_price,
                    max_price=max_price,
                    max_pages=max_pages
                )
                all_listings.extend(listings)
                # Save scraped leads
                save_scraped_leads(self.db, customer_id, lead_type="property", source="99acres", leads=listings)
        
        return all_listings
    
    def update_scraping_config(
        self,
        customer_id: int,
        magicbricks_enabled: bool = True,
        ninety_nine_acres_enabled: bool = True,
        scraping_interval: int = 24
    ) -> ScrapingConfig:
        """
        Update scraping configuration for a customer.
        
        Args:
            customer_id: ID of the customer
            magicbricks_enabled: Whether to enable MagicBricks scraping
            ninety_nine_acres_enabled: Whether to enable 99acres scraping
            scraping_interval: Interval between scrapes in hours
            
        Returns:
            Updated ScrapingConfig object
        """
        config = self.db.query(ScrapingConfig).filter(
            ScrapingConfig.customer_id == customer_id
        ).first()
        
        if not config:
            config = ScrapingConfig(
                customer_id=customer_id,
                magicbricks_enabled=magicbricks_enabled,
                ninety_nine_acres_enabled=ninety_nine_acres_enabled,
                scraping_interval=scraping_interval
            )
            self.db.add(config)
        else:
            config.magicbricks_enabled = magicbricks_enabled
            config.ninety_nine_acres_enabled = ninety_nine_acres_enabled
            config.scraping_interval = scraping_interval
        
        self.db.commit()
        self.db.refresh(config)
        
        return config

    async def scrape_users(self, customer_id: int, location: str = "", max_pages: int = 5) -> List[Dict]:
        users = []
        async with UserScraper() as scraper:
            users = await scraper.scrape_listings(location=location, max_pages=max_pages)
            save_scraped_leads(self.db, customer_id, lead_type="user", source="user_source", leads=users)
        return users

    async def scrape_locations(self, customer_id: int, max_pages: int = 5) -> List[Dict]:
        locations = []
        async with LocationScraper() as scraper:
            locations = await scraper.scrape_listings(max_pages=max_pages)
            save_scraped_leads(self.db, customer_id, lead_type="location", source="location_source", leads=locations)
        return locations

class MagicBricksScraper:
    def __init__(self):
        self.base_url = "https://www.magicbricks.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def scrape_listings(
        self,
        location: str,
        property_type: str = "residential",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        max_pages: int = 5
    ) -> List[Dict]:
        """
        Scrape property listings from MagicBricks.
        
        Args:
            location: Location to search in
            property_type: Type of property (residential/commercial)
            min_price: Minimum price filter
            max_price: Maximum price filter
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of property listings
        """
        listings = []
        page = 1
        
        try:
            while page <= max_pages:
                url = f"{self.base_url}/property-for-sale/residential-real-estate?bedroom=&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa&cityName={location}&page={page}"
                
                async with self.session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        break
                        
                    html = await response.text()
                    # TODO: Implement HTML parsing logic
                    # This is a placeholder for the actual parsing implementation
                    
                    # If no more listings found, break the loop
                    if not html:
                        break
                        
                    page += 1
                    
        except Exception as e:
            logger.error(f"Error scraping MagicBricks: {str(e)}")
            
        return listings

class NinetyNineAcresScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.99acres.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def scrape_listings(
        self,
        location: str,
        property_type: str = "residential",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        max_pages: int = 5
    ) -> List[Dict]:
        """
        Scrape property listings from 99acres.
        
        Args:
            location: Location to search in
            property_type: Type of property (residential/commercial)
            min_price: Minimum price filter
            max_price: Maximum price filter
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of property listings
        """
        listings = []
        page = 1
        
        try:
            while page <= max_pages:
                url = f"{self.base_url}/property-for-sale-in-{location}-ffid?page={page}"
                
                async with self.session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        break
                        
                    html = await response.text()
                    # TODO: Implement HTML parsing logic
                    # This is a placeholder for the actual parsing implementation
                    
                    # If no more listings found, break the loop
                    if not html:
                        break
                        
                    page += 1
                    
        except Exception as e:
            logger.error(f"Error scraping 99acres: {str(e)}")
            
        return listings

    def _parse_listings(self, html: str) -> List[Dict[str, Any]]:
        """Parse HTML and extract listing data."""
        # This is a placeholder - implement actual parsing logic
        return [] 