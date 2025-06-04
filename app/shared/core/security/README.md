# Security Package

This package contains all security-related functionality for the application.

## Components

### Authentication (`auth.py`)
- User authentication
- JWT token generation and validation
- User session management
- Multi-factor authentication

### Security Utilities (`security.py`)
- Password hashing and verification
- Token encryption/decryption
- Security headers
- CSRF protection

### JWT Management (`jwt.py`)
- JWT token generation
- Token validation
- Refresh token handling
- Token blacklisting

### Role Management (`roles.py`)
- Role definitions
- Role hierarchy
- Role assignment
- Role validation

### Permission Management (`permissions.py`)
- Permission definitions
- Permission checking
- Permission assignment
- Access control lists

### Password Utilities (`password_utils.py`)
- Password hashing
- Password validation
- Password reset
- Password policy enforcement

## Usage

```python
from app.shared.core.security import (
    get_current_user,
    verify_password,
    create_access_token,
    require_role
)

# Authentication
@router.post("/login")
async def login(user_data: UserLogin):
    user = authenticate_user(user_data)
    token = create_access_token(user)
    return {"token": token}

# Authorization
@router.get("/protected")
@require_role("admin")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": "Access granted"}
```

## Security Best Practices

1. Always use the provided security utilities instead of implementing custom solutions
2. Keep sensitive operations in this package
3. Use proper error handling for security-related operations
4. Log security events appropriately
5. Follow the principle of least privilege
6. Use secure defaults for all security settings 