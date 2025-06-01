import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.scraping.models.scraping import (
    ScrapingConfig,
    ScrapingJob,
    ScrapingResult,
    ScrapingSource,
    ScrapingStatus
)
from app.scraping.services.scraper import ScraperService
from app.scraping.services.scheduler import ScrapingScheduler
from app.shared.core.exceptions import NotFoundError, ValidationError

@pytest.fixture
 def db_session():
     """Create a test database session."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def scraper_service(db_session):
    """Create a scraper service instance."""
    return ScraperService(db_session)

@pytest.fixture
def scheduler_service(db_session):
    """Create a scheduler service instance."""
    return ScrapingScheduler(db_session)

@pytest.fixture
def test_config(db_session):
    """Create a test scraping configuration."""
    config = ScrapingConfig(
        id="test-config-id",
        customer_id="test-customer-id",
        enabled_sources=[ScrapingSource.MAGICBRICKS],
        locations=["Mumbai"],
        property_types=["Apartment"],
        price_range_min=1000000,
        price_range_max=5000000,
        max_pages_per_source=2,
        scraping_delay=1,
        max_retries=2,
        proxy_enabled=False,
        auto_scrape_enabled=True,
        auto_scrape_interval=24
    )
    db_session.add(config)
    db_session.commit()
    return config

@pytest.mark.asyncio
async def test_create_config(scraper_service, db_session):
    """Test creating a scraping configuration."""
    config_data = {
        "enabled_sources": [ScrapingSource.MAGICBRICKS],
        "locations": ["Mumbai"],
        "property_types": ["Apartment"],
        "price_range_min": 1000000,
        "price_range_max": 5000000,
        "max_pages_per_source": 2,
        "scraping_delay": 1,
        "max_retries": 2,
        "proxy_enabled": False,
        "auto_scrape_enabled": True,
        "auto_scrape_interval": 24
    }
    
    config = await scraper_service.create_config(config_data, "test-customer-id")
    
    assert config.customer_id == "test-customer-id"
    assert config.enabled_sources == [ScrapingSource.MAGICBRICKS]
    assert config.locations == ["Mumbai"]
    assert config.property_types == ["Apartment"]
    assert config.price_range_min == 1000000
    assert config.price_range_max == 5000000
    assert config.max_pages_per_source == 2
    assert config.scraping_delay == 1
    assert config.max_retries == 2
    assert config.proxy_enabled is False
    assert config.auto_scrape_enabled is True
    assert config.auto_scrape_interval == 24

@pytest.mark.asyncio
async def test_get_config(scraper_service, test_config):
    """Test getting a scraping configuration."""
    config = await scraper_service.get_config(test_config.id, test_config.customer_id)
    
    assert config.id == test_config.id
    assert config.customer_id == test_config.customer_id
    assert config.enabled_sources == test_config.enabled_sources
    assert config.locations == test_config.locations
    assert config.property_types == test_config.property_types

@pytest.mark.asyncio
async def test_update_config(scraper_service, test_config):
    """Test updating a scraping configuration."""
    update_data = {
        "locations": ["Mumbai", "Delhi"],
        "price_range_max": 6000000,
        "auto_scrape_interval": 12
    }
    
    updated_config = await scraper_service.update_config(
        test_config.id,
        update_data,
        test_config.customer_id
    )
    
    assert updated_config.locations == ["Mumbai", "Delhi"]
    assert updated_config.price_range_max == 6000000
    assert updated_config.auto_scrape_interval == 12

@pytest.mark.asyncio
async def test_delete_config(scraper_service, test_config, db_session):
    """Test deleting a scraping configuration."""
    await scraper_service.delete_config(test_config.id, test_config.customer_id)
    
    config = db_session.query(ScrapingConfig).filter(
        ScrapingConfig.id == test_config.id
    ).first()
    
    assert config is None

@pytest.mark.asyncio
async def test_run_scraping_job(scraper_service, test_config):
    """Test running a scraping job."""
    job = await scraper_service.run_scraping_job(
        test_config.id,
        ScrapingSource.MAGICBRICKS,
        "Mumbai",
        "Apartment"
    )
    
    assert job.config_id == test_config.id
    assert job.source == ScrapingSource.MAGICBRICKS
    assert job.location == "Mumbai"
    assert job.property_type == "Apartment"
    assert job.status in [ScrapingStatus.COMPLETED, ScrapingStatus.FAILED]

@pytest.mark.asyncio
async def test_list_jobs(scraper_service, test_config):
    """Test listing scraping jobs."""
    # Create some test jobs
    jobs = []
    for i in range(3):
        job = ScrapingJob(
            config_id=test_config.id,
            source=ScrapingSource.MAGICBRICKS,
            location="Mumbai",
            property_type="Apartment",
            status=ScrapingStatus.COMPLETED,
            items_scraped=10,
            completed_at=datetime.utcnow()
        )
        scraper_service.db.add(job)
        jobs.append(job)
    scraper_service.db.commit()
    
    # Test listing all jobs
    all_jobs = scraper_service.list_jobs(config_id=test_config.id)
    assert len(all_jobs) == 3
    
    # Test filtering by status
    completed_jobs = scraper_service.list_jobs(
        config_id=test_config.id,
        status=ScrapingStatus.COMPLETED
    )
    assert len(completed_jobs) == 3
    
    # Test filtering by date range
    start_date = datetime.utcnow() - timedelta(hours=1)
    end_date = datetime.utcnow() + timedelta(hours=1)
    date_filtered_jobs = scraper_service.list_jobs(
        config_id=test_config.id,
        start_date=start_date,
        end_date=end_date
    )
    assert len(date_filtered_jobs) == 3

@pytest.mark.asyncio
async def test_get_job_results(scraper_service, test_config):
    """Test getting job results."""
    # Create a test job
    job = ScrapingJob(
        config_id=test_config.id,
        source=ScrapingSource.MAGICBRICKS,
        location="Mumbai",
        property_type="Apartment",
        status=ScrapingStatus.COMPLETED,
        items_scraped=2,
        completed_at=datetime.utcnow()
    )
    scraper_service.db.add(job)
    scraper_service.db.commit()
    
    # Create test results
    results = []
    for i in range(2):
        result = ScrapingResult(
            job_id=job.id,
            title=f"Test Property {i}",
            description=f"Test Description {i}",
            price=1000000 + i * 500000,
            location="Mumbai",
            property_type="Apartment",
            bedrooms=2,
            bathrooms=2,
            area=1000,
            images=["test_image.jpg"],
            source_url="https://test.com",
            metadata={"test": "data"}
        )
        scraper_service.db.add(result)
        results.append(result)
    scraper_service.db.commit()
    
    # Test getting results
    job_results = scraper_service.get_job_results(job.id)
    assert len(job_results) == 2
    
    # Test pagination
    paginated_results = scraper_service.get_job_results(job.id, skip=1, limit=1)
    assert len(paginated_results) == 1

@pytest.mark.asyncio
async def test_get_scraping_stats(scraper_service, test_config):
    """Test getting scraping statistics."""
    # Create test jobs with different statuses
    jobs = [
        ScrapingJob(
            config_id=test_config.id,
            source=ScrapingSource.MAGICBRICKS,
            location="Mumbai",
            property_type="Apartment",
            status=ScrapingStatus.COMPLETED,
            items_scraped=10,
            completed_at=datetime.utcnow()
        ),
        ScrapingJob(
            config_id=test_config.id,
            source=ScrapingSource.MAGICBRICKS,
            location="Mumbai",
            property_type="Apartment",
            status=ScrapingStatus.FAILED,
            error_message="Test error",
            completed_at=datetime.utcnow()
        )
    ]
    for job in jobs:
        scraper_service.db.add(job)
    scraper_service.db.commit()
    
    # Get statistics
    stats = scraper_service.get_scraping_stats(test_config.id)
    
    assert stats["total_jobs"] == 2
    assert stats["completed_jobs"] == 1
    assert stats["failed_jobs"] == 1
    assert stats["total_items"] == 10
    assert stats["success_rate"] == 50.0
    assert stats["source_distribution"]["magicbricks"] == 2 