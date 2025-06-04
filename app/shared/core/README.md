# Shared Core Package

This package contains shared core functionality used across the application. It is organized into several subpackages:

## Security (`security/`)

Core security functionality including:
- Authentication and authorization
- JWT token management
- Password hashing and verification
- Role-based access control (RBAC)
- Permission management

Key modules:
- `auth.py`: Authentication logic
- `security.py`: Security utilities
- `jwt.py`: JWT token handling
- `roles.py`: Role definitions
- `permissions.py`: Permission management
- `password_utils.py`: Password handling utilities

## Communication (`communication/`)

Communication-related functionality:
- Email sending
- SMS messaging
- Message templates
- Outreach automation

Key modules:
- `email.py`: Email sending functionality
- `sms.py`: SMS messaging
- `messages.py`: Message templates and localization
- `outreach.py`: Outreach automation engine

## Infrastructure (`infrastructure/`)

Core infrastructure components:
- Database dependencies
- Logging configuration
- Rate limiting
- CAPTCHA verification
- Middleware components

Key modules:
- `deps.py`: Database and dependency injection
- `logging.py`: Logging configuration
- `rate_limit.py`: Rate limiting implementation
- `captcha.py`: CAPTCHA verification
- `middleware.py`: Common middleware components

## Common Utilities

Shared utilities used across the application:
- `config.py`: Application configuration
- `exceptions.py`: Custom exceptions
- `pagination.py`: Pagination utilities
- `audit.py`: Audit logging

## Usage

Import from the appropriate subpackage:

```python
# Security
from app.shared.core.security import get_current_user, verify_password

# Communication
from app.shared.core.communication import send_email, send_sms

# Infrastructure
from app.shared.core.infrastructure import get_db, setup_logging

# Common utilities
from app.shared.core import config, exceptions, pagination
```

## Best Practices

1. Always use the shared core components instead of implementing duplicate functionality
2. Keep security-sensitive operations in the security package
3. Use the audit logging for important operations
4. Follow the established patterns for error handling and validation
5. Use the provided dependency injection system for database access

## Contributing

When adding new functionality to these modules:

1. Follow the existing patterns and conventions
2. Add proper type hints and documentation
3. Include unit tests
4. Update this README if necessary
5. Consider the impact on existing code
6. Get code review before merging 