import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
import requests
from app.services.scraper import (
    BaseScraper,
    MagicBricksScraper,
    HousingScraper,
    PropTigerScraper,
    CommonFloorScraper,
    ScraperService
)
from app.shared.models.scraping import ScrapingConfig
from datetime import datetime
import asyncio

# Test data
MOCK_HTML = """
<div class="property-card">
    <h3 class="property-name">Test Property</h3>
    <div class="price">₹50,00,000</div>
    <div class="area">2000 sq.ft</div>
    <div class="builder-name">Test Builder</div>
    <div class="possession">Ready to Move</div>
</div>
"""

@pytest.fixture
def mock_config():
    return ScrapingConfig(
        id="test-id",
        customer_id="test-customer",
        enabled_sources=["magicbricks", "housing", "proptiger", "commonfloor"],
        locations=["Mumbai", "Delhi"],
        property_types=["Apartment", "Villa"],
        max_pages_per_source=2,
        scraping_delay=1,
        rate_limit=10,
        retry_count=3,
        timeout=30,
        proxy_enabled=False,
        proxy_url=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_response():
    response = Mock()
    response.text = MOCK_HTML
    response.status_code = 200
    return response

class TestBaseScraper:
    def test_init(self, mock_config):
        scraper = BaseScraper(mock_config)
        assert scraper.config == mock_config
        assert scraper.rate_limit == 10
        assert scraper.retry_count == 3
        assert scraper.timeout == 30

    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get, mock_config, mock_response):
        mock_get.return_value = mock_response
        scraper = BaseScraper(mock_config)
        response = scraper._make_request("http://test.com")
        assert response == mock_response
        mock_get.assert_called_once()

    @patch('requests.Session.get')
    def test_make_request_failure(self, mock_get, mock_config):
        mock_get.side_effect = requests.RequestException("Test error")
        scraper = BaseScraper(mock_config)
        with pytest.raises(requests.RequestException):
            scraper._make_request("http://test.com")

class TestMagicBricksScraper:
    @patch('app.services.scraper.BaseScraper._make_request')
    def test_scrape_properties(self, mock_make_request, mock_config, mock_response):
        mock_make_request.return_value = mock_response
        scraper = MagicBricksScraper(mock_config)
        properties = scraper.scrape_properties("Mumbai", "Apartment")
        assert len(properties) > 0
        assert properties[0]['name'] == "Test Property"

class TestHousingScraper:
    @patch('app.services.scraper.BaseScraper._make_request')
    def test_scrape_properties(self, mock_make_request, mock_config, mock_response):
        mock_make_request.return_value = mock_response
        scraper = HousingScraper(mock_config)
        properties = scraper.scrape_properties("Mumbai", "Apartment")
        assert len(properties) > 0
        assert properties[0]['name'] == "Test Property"

class TestPropTigerScraper:
    @patch('app.services.scraper.BaseScraper._make_request')
    def test_scrape_properties(self, mock_make_request, mock_config, mock_response):
        mock_make_request.return_value = mock_response
        scraper = PropTigerScraper(mock_config)
        properties = scraper.scrape_properties("Mumbai", "Apartment")
        assert len(properties) > 0
        assert properties[0]['name'] == "Test Property"

class TestCommonFloorScraper:
    @patch('app.services.scraper.BaseScraper._make_request')
    def test_scrape_properties(self, mock_make_request, mock_config, mock_response):
        mock_make_request.return_value = mock_response
        scraper = CommonFloorScraper(mock_config)
        properties = scraper.scrape_properties("Mumbai", "Apartment")
        assert len(properties) > 0
        assert properties[0]['name'] == "Test Property"

class TestScraperService:
    def test_init(self, mock_db):
        service = ScraperService(mock_db)
        assert service.db == mock_db
        assert len(service.scrapers) == 4

    def test_get_scraper(self, mock_db, mock_config):
        service = ScraperService(mock_db)
        scraper = service.get_scraper("magicbricks", mock_config)
        assert isinstance(scraper, MagicBricksScraper)

    def test_get_scraper_invalid_source(self, mock_db, mock_config):
        service = ScraperService(mock_db)
        with pytest.raises(ValueError):
            service.get_scraper("invalid_source", mock_config)

    @pytest.mark.asyncio
    async def test_scrape_all_sources_async(self, mock_db, mock_config):
        service = ScraperService(mock_db)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_config
        
        with patch.object(service, '_scrape_source_async') as mock_scrape:
            mock_scrape.return_value = {
                'source': 'MagicBricksScraper',
                'location': 'Mumbai',
                'property_type': 'Apartment',
                'properties': [{'name': 'Test Property'}],
                'status': 'success'
            }
            
            results = await service.scrape_all_sources_async("test-customer")
            assert len(results) > 0
            assert 'MagicBricksScraper' in results

    def test_schedule_scraping(self, mock_db, mock_config):
        service = ScraperService(mock_db)
        service.schedule_scraping("test-customer", 24)
        assert service.scheduler.get_job("scraping_test-customer") is not None

    def test_stop_scraping(self, mock_db, mock_config):
        service = ScraperService(mock_db)
        service.schedule_scraping("test-customer", 24)
        service.stop_scraping("test-customer")
        assert service.scheduler.get_job("scraping_test-customer") is None

@pytest.mark.asyncio
async def test_async_request():
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = asyncio.Future()
        mock_response.text.set_result("Test response")
        mock_get.return_value.__aenter__.return_value = mock_response
        
        scraper = BaseScraper(Mock())
        result = await scraper._make_async_request("http://test.com")
        assert result == "Test response"

def test_process_async_results():
    service = ScraperService(Mock())
    results = [
        {
            'source': 'MagicBricksScraper',
            'properties': [{'name': 'Property 1'}]
        },
        {
            'source': 'HousingScraper',
            'properties': [{'name': 'Property 2'}]
        }
    ]
    
    processed = service._process_async_results(results)
    assert 'MagicBricksScraper' in processed
    assert 'HousingScraper' in processed
    assert len(processed['MagicBricksScraper']) == 1
    assert len(processed['HousingScraper']) == 1 