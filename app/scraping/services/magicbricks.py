import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from app.scraping.models.scraping import ScrapingSource
from app.scraping.services.base import BaseScraper
from datetime import datetime
from typing import Dict
from typing import Any
from app.shared.core.logging import logger
from datetime import datetime
from typing import Dict
from typing import Any
from app.shared.core.logging import logger

logger = logging.getLogger(__name__)

class MagicBricksScraper(BaseScraper):
    """Scraper implementation for MagicBricks.com"""

    BASE_URL = "https://www.magicbricks.com/property-for-sale/residential-real-estate"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source = ScrapingSource.MAGICBRICKS

    async def scrape(self, location: str, property_type: str) -> List[Dict[str, Any]]:
        """Scrape properties from MagicBricks."""
        results = []
        page = 1
        max_pages = self.config.max_pages_per_source

        while page <= max_pages:
            url = self._build_url(location, property_type, page)
            html = await self.make_request(url)
            
            if not html:
                logger.error(f"Failed to fetch page {page} for {location}")
                break

            properties = self._parse_properties(html)
            if not properties:
                break

            results.extend(properties)
            page += 1

            # Respect scraping delay
            await asyncio.sleep(self.config.scraping_delay)

        return results

    def _build_url(self, location: str, property_type: str, page: int) -> str:
        """Build MagicBricks URL with search parameters."""
        params = {
            'bedroom': self._get_bedroom_param(property_type),
            'proptype': self._get_property_type_param(property_type),
            'cityName': location,
            'page': page
        }
        
        query_string = '&'.join(f"{k}={v}" for k, v in params.items() if v)
        return f"{self.BASE_URL}?{query_string}"

    def _get_bedroom_param(self, property_type: str) -> Optional[str]:
        """Convert property type to bedroom parameter."""
        bedroom_map = {
            '1BHK': '1',
            '2BHK': '2',
            '3BHK': '3',
            '4BHK': '4',
            '5BHK': '5'
        }
        return bedroom_map.get(property_type)

    def _get_property_type_param(self, property_type: str) -> Optional[str]:
        """Convert property type to MagicBricks property type parameter."""
        type_map = {
            'Apartment': 'Apartment',
            'Villa': 'Villa',
            'Plot': 'Plot',
            'House': 'Independent House'
        }
        return type_map.get(property_type)

    def _parse_properties(self, html: str) -> List[Dict[str, Any]]:
        """Parse property listings from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        properties = []

        for listing in soup.select('.m-srp-card'):
            try:
                property_data = self._parse_property(listing)
                if property_data:
                    properties.append(property_data)
            except Exception as e:
                logger.error(f"Failed to parse property listing: {str(e)}")
                continue

        return properties

    def _parse_property(self, listing) -> Optional[Dict[str, Any]]:
        """Parse individual property listing."""
        try:
            # Extract basic information
            title = listing.select_one('.m-srp-card__title').text.strip()
            price = self._parse_price(listing.select_one('.m-srp-card__price').text)
            location = listing.select_one('.m-srp-card__address').text.strip()
            
            # Extract property details
            details = listing.select('.m-srp-card__summary__item')
            bedrooms = self._extract_detail(details, 'Bedroom')
            bathrooms = self._extract_detail(details, 'Bathroom')
            area = self._extract_area(listing.select_one('.m-srp-card__area').text)
            
            # Extract images
            images = [
                img['src'] for img in listing.select('.m-srp-card__photo img')
                if img.get('src')
            ]

            # Extract source URL
            source_url = listing.select_one('a.m-srp-card__link')['href']
            if not source_url.startswith('http'):
                source_url = f"https://www.magicbricks.com{source_url}"

            return {
                'title': title,
                'price': price,
                'location': location,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'area': area,
                'images': images,
                'source_url': source_url,
                'source': self.source,
                'metadata': {
                    'posted_date': self._parse_date(listing.select_one('.m-srp-card__date').text),
                    'property_id': self._extract_property_id(source_url)
                }
            }
        except Exception as e:
            logger.error(f"Error parsing property: {str(e)}")
            return None

    def _parse_price(self, price_text: str) -> float:
        """Parse price from text."""
        try:
            price_text = re.sub(r'[^\d.]', '', price_text)
            return float(price_text)
        except (ValueError, TypeError):
            return 0.0

    def _extract_detail(self, details, key: str) -> Optional[int]:
        """Extract numeric detail from property details."""
        for detail in details:
            if key in detail.text:
                return self._parse_numeric_detail(detail.text)
        return None

    def _parse_numeric_detail(self, detail: str) -> Optional[int]:
        """Parse numeric detail from text."""
        try:
            return int(re.search(r'\d+', detail).group())
        except (ValueError, TypeError, AttributeError):
            return None

    def _extract_area(self, area_text: str) -> Optional[float]:
        """Extract area in square feet."""
        try:
            area = float(re.search(r'(\d+)\s*sq\.ft', area_text).group(1))
            if 'sq.m' in area_text.lower():
                area *= 10.764
            return area
        except (ValueError, TypeError, AttributeError):
            return None

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from text."""
        try:
            if not date_text.strip():
                return datetime.utcnow()
            return datetime.strptime(date_text.strip(), '%d %b %Y')
        except (ValueError, TypeError):
            return None

    def _extract_property_id(self, url: str) -> Optional[str]:
        """Extract property ID from URL."""
        try:
            match = re.search(r'/(\d+)(?:/|$)', url)
            return match.group(1) if match else None
        except (AttributeError, IndexError):
            return None 