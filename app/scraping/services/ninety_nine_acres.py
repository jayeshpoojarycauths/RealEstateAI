import re
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import Browser, Page, async_playwright

from .base import BaseScraper
from typing import Dict
from typing import Any
from app.shared.core.logging import logger
from typing import Dict
from typing import Any
from app.shared.core.logging import logger


class NinetyNineAcresScraper(BaseScraper):
    BASE_URL = "https://www.99acres.com"
    SEARCH_URL = f"{BASE_URL}/property-for-sale-rent-in-mumbai-ffid"

    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape property listings from 99acres"""
        async with async_playwright() as p:
            browser = await self._launch_browser(p)
            try:
                page = await browser.new_page()
                projects = []
                
                # Navigate to search page
                await page.goto(self.SEARCH_URL)
                await page.wait_for_selector('.propertyCard')

                # Get total pages
                total_pages = await self._get_total_pages(page)
                
                # Scrape each page
                for page_num in range(1, total_pages + 1):
                    if page_num > 1:
                        await page.goto(f"{self.SEARCH_URL}?page={page_num}")
                        await page.wait_for_selector('.propertyCard')
                    
                    # Extract property cards
                    cards = await page.query_selector_all('.propertyCard')
                    for card in cards:
                        try:
                            project = await self._extract_property_data(card)
                            if project:
                                projects.append(project)
                        except Exception as e:
                            self.logger.error(f"Failed to extract property data: {str(e)}")
                            continue

                return projects
            finally:
                await browser.close()

    async def _launch_browser(self, playwright) -> Browser:
        """Launch browser with proxy if available"""
        proxy = self.get_random_proxy()
        browser_args = []
        
        if proxy:
            browser_args.append(f'--proxy-server={proxy}')
        
        return await playwright.chromium.launch(
            headless=True,
            args=browser_args
        )

    async def _get_total_pages(self, page: Page) -> int:
        """Get total number of pages from pagination"""
        try:
            pagination = await page.query_selector('.pagination')
            if not pagination:
                return 1
            
            last_page = await pagination.query_selector('li:last-child')
            if last_page:
                text = await last_page.text_content()
                return int(text.strip())
            return 1
        except Exception:
            return 1

    async def _extract_property_data(self, card) -> Optional[Dict[str, Any]]:
        """Extract property data from a card element"""
        try:
            # Extract basic info
            title = await card.query_selector('.propertyCard__title')
            title_text = await title.text_content() if title else ''
            
            price = await card.query_selector('.propertyCard__price')
            price_text = await price.text_content() if price else ''
            price_value = self.parse_price(price_text)
            
            location = await card.query_selector('.propertyCard__location')
            location_text = await location.text_content() if location else ''
            
            # Extract details
            details = await card.query_selector('.propertyCard__details')
            details_text = await details.text_content() if details else ''
            bedrooms, bathrooms, area = self.parse_property_details(details_text)
            
            # Get property URL
            link = await card.query_selector('a')
            url = await link.get_attribute('href') if link else ''
            full_url = f"{self.BASE_URL}{url}" if url else ''
            
            # Get images
            image = await card.query_selector('img')
            image_url = await image.get_attribute('src') if image else ''
            
            return {
                'title': title_text.strip(),
                'price': price_value,
                'location': location_text.strip(),
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'area': area,
                'source': '99acres',
                'source_url': full_url,
                'images': [image_url] if image_url else [],
                'metadata': {
                    'raw_price': price_text.strip(),
                    'raw_details': details_text.strip()
                }
            }
        except Exception as e:
            self.logger.error(f"Error extracting property data: {str(e)}")
            return None

    def parse_price(self, price_text: str) -> float:
        """Parse price from text."""
        try:
            price = re.sub(r'[^\d.]', '', price_text)
            return float(price)
        except (ValueError, TypeError):
            return 0.0

    def parse_property_details(self, details_text: str) -> Tuple[int, int, float]:
        """Parse property details from text."""
        try:
            parts = details_text.split('•')
            bedrooms = int(re.search(r'\d+', parts[0]).group())
            bathrooms = int(re.search(r'\d+', parts[1]).group())
            area = float(re.search(r'(\d+)\s*sq\.ft', parts[2]).group(1)) if len(parts) > 2 else 0
            return bedrooms, bathrooms, area
        except (ValueError, TypeError, AttributeError, IndexError):
            return 0, 0, 0

    async def _make_request_impl(self, url: str, headers: Dict[str, str], proxy: Optional[str]) -> Any:
        """Implementation of HTTP request using Playwright"""
        async with async_playwright() as p:
            browser = await self._launch_browser(p)
            try:
                page = await browser.new_page()
                if headers:
                    await page.set_extra_http_headers(headers)
                response = await page.goto(url)
                return await response.text()
            finally:
                await browser.close() 