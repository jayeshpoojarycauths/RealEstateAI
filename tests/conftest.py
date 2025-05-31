import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.shared.core.config import Settings
from app.models.models import User, Customer, Role, Permission, ScrapingConfig
from datetime import datetime
import uuid

# Create test settings instance
test_settings = Settings(
    _env_file=".env.test",  # Use test environment file
    POSTGRES_DB="test_db",  # Override database name for tests
    DB_ECHO=False  # Disable SQL echo during tests
)

@pytest.fixture(scope="session")
def engine():
    return create_engine(test_settings.get_database_url)

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    """Creates a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def test_customer(db_session):
    customer = Customer(
        id=str(uuid.uuid4()),
        name="Test Company",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(customer)
    db_session.commit()
    return customer

@pytest.fixture
def test_user(db_session, test_customer):
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        customer_id=test_customer.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_role(db_session, test_customer):
    role = Role(
        id=str(uuid.uuid4()),
        name="Test Role",
        description="Test Role Description",
        customer_id=test_customer.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(role)
    db_session.commit()
    return role

@pytest.fixture
def test_permission(db_session):
    permission = Permission(
        id=str(uuid.uuid4()),
        name="test_permission",
        description="Test Permission",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(permission)
    db_session.commit()
    return permission

@pytest.fixture
def test_scraping_config(db_session, test_customer):
    config = ScrapingConfig(
        id=str(uuid.uuid4()),
        customer_id=test_customer.id,
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
    db_session.add(config)
    db_session.commit()
    return config

@pytest.fixture
def mock_settings():
    return {
        "PROJECT_NAME": "Real Estate CRM",
        "VERSION": "1.0.0",
        "API_V1_STR": "/api/v1",
        "BACKEND_CORS_ORIGINS": ["http://localhost:3000"],
        "SECRET_KEY": "test_secret_key",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        "DATABASE_URL": test_settings.get_database_url
    } 