# Real Estate CRM - Multi-Tenant AI Outreach & Scraping System

A multi-tenant Real Estate CRM application that enables AI-powered communication and property lead scraping for multiple customers (firms).

## Features

- Multi-tenant architecture with tenant isolation
- Lead management with AI-powered outreach
- Real estate property scraping
- Role-based access control (RBAC)
- Multiple communication channels (SMS, Email, WhatsApp, Telegram)
- Automated scraping scheduler

## Tech Stack

- Backend: FastAPI + PostgreSQL + SQLAlchemy
- Frontend: Streamlit
- Authentication: JWT-based
- Scraping: BeautifulSoup + Selenium
- Communication: Twilio (SMS/call), SendGrid (email)
- Task Scheduler: Celery/APScheduler

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=real_estate_crm
SECRET_KEY=your_secret_key
SENDGRID_API_KEY=your_sendgrid_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
```

4. Initialize the database:
```bash
alembic upgrade head
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Multi-Tenant Architecture

The system uses a shared database with tenant isolation through the `customer_id` foreign key in all relevant tables. Each tenant (customer) has their own:
- Users
- Roles and permissions
- Leads
- Real estate projects
- Outreach logs

## Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- Tenant isolation at the database level

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Testing

### Setup

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Create a test database:
```bash
# For PostgreSQL
createdb real_estate_test

# For SQLite (default for tests)
# No setup needed, tests will create the database automatically
```

### Running Tests

#### Basic Test Commands

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app

# Run tests in parallel
pytest -n auto

# Run tests with HTML report
pytest --html=report.html
```

#### Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run only scraping tests
pytest -m scraping

# Run only database tests
pytest -m db

# Run all tests except slow ones
pytest -m "not slow"
```

#### Debugging Tests

```bash
# Run tests with detailed output
pytest -v

# Show print statements
pytest -s

# Run specific test file
pytest tests/test_scraper.py

# Run specific test function
pytest tests/test_scraper.py::test_magicbricks_scraper

# Run tests with debugger on failure
pytest --pdb
```

#### Test Reports

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Generate test report
pytest --html=report.html

# Show slowest tests
pytest --durations=10
```

### Test Configuration

The project uses `pytest.ini` for test configuration. Key settings include:

- Test file patterns: `test_*.py`, `*_test.py`
- Test markers for different test types
- Coverage reporting
- Environment variables
- Logging settings
- Timeout settings
- Parallel execution settings

### Writing Tests

1. Place test files in the `tests` directory
2. Name test files with `test_` prefix
3. Use appropriate markers for test categorization
4. Follow the test naming convention:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test functions: `test_*`

Example test structure:
```python
import pytest

@pytest.mark.unit
def test_some_function():
    # Test code here
    pass

@pytest.mark.integration
class TestSomeFeature:
    def test_feature_behavior(self):
        # Test code here
        pass
```

### Continuous Integration

The project includes GitHub Actions workflows for:
- Running tests on push and pull requests
- Generating and uploading coverage reports
- Running linting and type checking 