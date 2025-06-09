"""
Constants Module

This module defines all system-wide constants used throughout the Real Estate AI platform.
Constants are organized by category and include configuration values, enums, and message templates.

Categories:
- API: API-related configuration
- Security: Authentication and authorization settings
- Rate Limiting: API rate limiting thresholds
- Cache: Caching configuration
- File Upload: File upload restrictions
- Pagination: Default pagination settings
- Search: Search-related parameters
- Notifications: Notification type definitions
- Property: Property-related enums and constants
- Currency: Supported currencies
- Measurement: Measurement units
- Time Zone: Time zone settings
- Messages: Error and success message templates

Usage:
    from app.shared.core.constants import API_PREFIX, PropertyStatus, Currency

    @router.get(f"{API_PREFIX}/properties")
    async def get_properties(status: PropertyStatus = PropertyStatus.ACTIVE):
        return {"status": status, "currency": Currency.USD}
"""

from enum import Enum

# API Constants
API_PREFIX = "/api/v1"
API_TITLE = "Real Estate AI API"
API_DESCRIPTION = "API for Real Estate AI Platform"
API_VERSION = "1.0.0"

# Security Constants
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Rate Limiting Constants
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000
RATE_LIMIT_PER_DAY = 10000

# Cache Constants
CACHE_TTL = 3600  # 1 hour in seconds
CACHE_PREFIX = "real_estate_ai:"

# File Upload Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
ALLOWED_DOCUMENT_TYPES = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

# Pagination Constants
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Search Constants
DEFAULT_SEARCH_RADIUS = 5  # kilometers
MAX_SEARCH_RADIUS = 50  # kilometers

# Notification Constants
NOTIFICATION_TYPES = {
    "PROPERTY_VIEW": "property_view",
    "PROPERTY_FAVORITE": "property_favorite",
    "PROPERTY_CONTACT": "property_contact",
    "PROPERTY_UPDATE": "property_update",
    "SYSTEM_ALERT": "system_alert"
}

# Property Status Constants
class PropertyStatus(str, Enum):
    """
    Property status enumeration.
    
    Defines the possible states a property can be in:
    - ACTIVE: Property is available for viewing/booking
    - PENDING: Property is under review or processing
    - SOLD: Property has been sold
    - RENTED: Property has been rented
    - INACTIVE: Property is temporarily unavailable
    """
    ACTIVE = "active"
    PENDING = "pending"
    SOLD = "sold"
    RENTED = "rented"
    INACTIVE = "inactive"

# Property Type Constants
class PropertyType(str, Enum):
    """
    Property type enumeration.
    
    Defines the different types of properties in the system:
    - HOUSE: Single-family house
    - APARTMENT: Apartment unit
    - CONDO: Condominium
    - TOWNHOUSE: Townhouse
    - LAND: Vacant land
    - COMMERCIAL: Commercial property
    """
    HOUSE = "house"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    LAND = "land"
    COMMERCIAL = "commercial"

# Currency Constants
class Currency(str, Enum):
    """
    Currency enumeration.
    
    Defines the supported currencies for property prices:
    - USD: US Dollar
    - EUR: Euro
    - GBP: British Pound
    - CAD: Canadian Dollar
    - AUD: Australian Dollar
    """
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"

# Measurement Unit Constants
class MeasurementUnit(str, Enum):
    """
    Measurement unit enumeration.
    
    Defines the supported units for property measurements:
    - SQUARE_FEET: Square feet (sqft)
    - SQUARE_METERS: Square meters (sqm)
    - ACRES: Acres
    - HECTARES: Hectares
    """
    SQUARE_FEET = "sqft"
    SQUARE_METERS = "sqm"
    ACRES = "acres"
    HECTARES = "hectares"

# Time Zone Constants
DEFAULT_TIMEZONE = "UTC"
SUPPORTED_TIMEZONES = [
    "UTC",
    "America/New_York",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Asia/Tokyo",
    "Australia/Sydney"
]

# Error Message Constants
ERROR_MESSAGES = {
    "INVALID_CREDENTIALS": "Invalid username or password",
    "UNAUTHORIZED": "Unauthorized access",
    "FORBIDDEN": "Access forbidden",
    "NOT_FOUND": "Resource not found",
    "VALIDATION_ERROR": "Validation error",
    "SERVER_ERROR": "Internal server error"
}

# Success Message Constants
SUCCESS_MESSAGES = {
    "CREATED": "Resource created successfully",
    "UPDATED": "Resource updated successfully",
    "DELETED": "Resource deleted successfully",
    "OPERATION_SUCCESS": "Operation completed successfully"
} 