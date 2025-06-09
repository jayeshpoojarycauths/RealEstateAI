import re
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import Page, async_playwright
from sqlalchemy.orm import Session

from app.shared.core.config import settings
from app.shared.models.customer import Customer

from .base import BaseScraper
from sqlalchemy.orm import Session
from typing import Dict
from typing import Any
from app.shared.core.logging import logger
from sqlalchemy.orm import Session
from typing import Dict
from typing import Any
from app.shared.core.logging import logger


class FacebookMarketplaceScraper(BaseScraper):
    BASE_URL = "https://www.facebook.com"
    MARKETPLACE_URL = f"{BASE_URL}/marketplace/category/propertyrentals"
    
    def __init__(self, db: Session, customer: Customer):
        super().__init__(db, customer)
        self.fb_email = settings.FB_EMAIL
        self.fb_password = settings.FB_PASSWORD
        self.session_cookie = None

    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape property listings from Facebook Marketplace"""
        async with async_playwright() as p:
            browser = await self._launch_browser(p)
            try:
                page = await browser.new_page()
                
                # Login if needed
                if not self.session_cookie:
                    await self._login(page)
                
                # Navigate to marketplace
                await page.goto(self.MARKETPLACE_URL)
                await page.wait_for_selector('[role="main"]')
                
                # Scroll to load more items
                await self._scroll_to_load_more(page)
                
                # Extract listings
                listings = await page.query_selector_all('[role="article"]')
                projects = []
                
                for listing in listings:
                    try:
                        project = await self._extract_listing_data(listing)
                        if project:
                            projects.append(project)
                    except Exception as e:
                        self.logger.error(f"Failed to extract listing data: {str(e)}")
                        continue
                
                return projects
            finally:
                await browser.close()

    async def _login(self, page: Page) -> None:
        """Login to Facebook"""
        try:
            await page.goto(f"{self.BASE_URL}/login")
            await page.wait_for_selector('#email')
            
            # Enter credentials
            await page.fill('#email', self.fb_email)
            await page.fill('#pass', self.fb_password)
            await page.click('button[name="login"]')
            
            # Wait for login to complete
            await page.wait_for_selector('[role="main"]')
            
            # Save session cookie
            cookies = await page.context.cookies()
            self.session_cookie = cookies
        except Exception as e:
            self.logger.error(f"Failed to login to Facebook: {str(e)}")
            raise

    async def _scroll_to_load_more(self, page: Page, max_scrolls: int = 5) -> None:
        """Scroll page to load more listings"""
        for _ in range(max_scrolls):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)  # Wait for content to load

    async def _extract_listing_data(self, listing) -> Optional[Dict[str, Any]]:
        """Extract data from a marketplace listing"""
        try:
            # Extract title and link
            title_elem = await listing.query_selector('span[dir="auto"]')
            title = await title_elem.text_content() if title_elem else ''
            
            link_elem = await listing.query_selector('a')
            url = await link_elem.get_attribute('href') if link_elem else ''
            
            # Extract price
            price_elem = await listing.query_selector('span[dir="auto"]:has-text("$")')
            price_text = await price_elem.text_content() if price_elem else ''
            price = self.parse_price(price_text)
            
            # Extract location
            location_elem = await listing.query_selector('span[dir="auto"]:has-text(",")')
            location = await location_elem.text_content() if location_elem else ''
            
            # Extract images
            image_elem = await listing.query_selector('img')
            image_url = await image_elem.get_attribute('src') if image_elem else ''
            
            # Extract description
            desc_elem = await listing.query_selector('div[dir="auto"]')
            description = await desc_elem.text_content() if desc_elem else ''
            
            # Extract details from description
            bedrooms, bathrooms, area = self.parse_property_details(description)
            
            return {
                'title': title.strip(),
                'price': price,
                'location': location.strip(),
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'area': area,
                'description': description.strip(),
                'source': 'facebook_marketplace',
                'source_url': url,
                'images': [image_url] if image_url else [],
                'metadata': {
                    'raw_price': price_text.strip(),
                    'raw_description': description.strip()
                }
            }
        except Exception as e:
            self.logger.error(f"Error extracting listing data: {str(e)}")
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
                if self.session_cookie:
                    await page.context.add_cookies(self.session_cookie)
                if headers:
                    await page.set_extra_http_headers(headers)
                response = await page.goto(url)
                return await response.text()
            finally:
                await browser.close() 