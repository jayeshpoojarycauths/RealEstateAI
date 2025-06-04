# Infrastructure Package

This package contains core infrastructure components and utilities used throughout the application.

## Components

### Dependencies (`deps.py`)
- Database session management
- User context injection
- Customer context injection
- Tenant context management
- Dependency injection utilities

### Logging (`logging.py`)
- Logging configuration
- Log formatting
- Log levels
- Log rotation
- Log aggregation

### Rate Limiting (`rate_limit.py`)
- Request rate limiting
- IP-based limiting
- User-based limiting
- Custom rate limit rules
- Rate limit storage

### CAPTCHA (`captcha.py`)
- CAPTCHA generation
- CAPTCHA verification
- CAPTCHA configuration
- CAPTCHA storage
- CAPTCHA cleanup

### Middleware (`middleware.py`)
- Request/response middleware
- Error handling
- Security headers
- CORS configuration
- Request logging

## Usage

```python
from app.shared.core.infrastructure import (
    get_db,
    setup_logging,
    RateLimiter,
    verify_captcha
)

# Database session
@router.get("/items")
async def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()

# Rate limiting
rate_limiter = RateLimiter()
@router.post("/api")
@rate_limiter.limit("10/minute")
async def api_endpoint():
    return {"message": "Success"}

# CAPTCHA verification
@router.post("/register")
async def register(captcha_token: str):
    if not verify_captcha(captcha_token):
        raise ValidationError("Invalid CAPTCHA")
    # Continue with registration
```

## Best Practices

1. Use dependency injection for database access
2. Configure appropriate logging levels
3. Implement proper rate limiting
4. Use CAPTCHA for sensitive operations
5. Follow middleware best practices
6. Handle errors appropriately
7. Use proper security headers
8. Implement proper cleanup routines 