# API Documentation

## Base URL
All API endpoints are prefixed with the base URL configured in the environment:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Authentication
All endpoints except `/auth/login` and `/auth/register` require authentication using a Bearer token. The token should be included in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user
- `POST /auth/verify-email` - Verify email address
- `POST /auth/resend-verification` - Resend verification email
- `POST /auth/reset-password` - Reset password

### Users
- `GET /users` - List users
- `POST /users` - Create user
- `GET /users/:id` - Get user by ID
- `PUT /users/:id` - Update user
- `DELETE /users/:id` - Delete user
- `GET /users/me` - Get current user profile
- `PUT /users/me/password` - Update password

### Properties
- `GET /properties` - List properties
- `POST /properties` - Create property
- `GET /properties/:id` - Get property by ID
- `PUT /properties/:id` - Update property
- `DELETE /properties/:id` - Delete property
- `GET /properties/stats` - Get property statistics

### Customers
- `GET /customers` - List customers
- `POST /customers` - Create customer
- `GET /customers/:id` - Get customer by ID
- `PUT /customers/:id` - Update customer
- `DELETE /customers/:id` - Delete customer

### Analytics
- `GET /analytics` - Get analytics overview
- `GET /analytics/lead-scores` - Get lead score analytics
- `GET /analytics/conversion-funnel` - Get conversion funnel data
- `GET /analytics/price-trends` - Get property price trends

### Platform (Admin Only)
- `GET /platform/tenants` - List tenants
- `POST /platform/tenants` - Create tenant
- `GET /platform/settings` - Get system settings
- `PUT /platform/settings` - Update system settings

### Audit
- `GET /audit/logs` - Get audit logs

## Role-Based Access Control

The API implements role-based access control with the following roles:
- `PLATFORM_ADMIN` - Platform-level administration
- `SUPERADMIN` - Tenant-level super administration
- `ADMIN` - Tenant-level administration
- `MANAGER` - Property management
- `AGENT` - Property agent
- `ANALYST` - Analytics access
- `AUDITOR` - Audit log access

Each endpoint has specific role requirements that are enforced by the API.

## Error Handling

The API uses standard HTTP status codes and returns error responses in the following format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {} // Optional additional error details
  }
}
```

## Rate Limiting

API requests are rate-limited based on the following configuration:
- `VITE_API_RATE_LIMIT`: Maximum requests per window (default: 100)
- `VITE_API_RATE_WINDOW`: Time window in milliseconds (default: 60000)

## File Upload

File uploads are subject to the following restrictions:
- `VITE_MAX_FILE_SIZE`: Maximum file size in bytes (default: 10MB)
- `VITE_ALLOWED_FILE_TYPES`: Comma-separated list of allowed MIME types 