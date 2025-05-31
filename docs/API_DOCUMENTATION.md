# API Documentation

## Authentication

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}
```

Response:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "roles": ["admin"]
    }
}
```

### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

Response:
```json
{
    "id": 1,
    "email": "user@example.com",
    "roles": ["admin"]
}
```

## Projects

### List Projects
```http
GET /api/v1/projects/
Authorization: Bearer <token>
```

Query Parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `status`: Filter by status
- `type`: Filter by type
- `search`: Search in name and description

Response:
```json
{
    "items": [
        {
            "id": 1,
            "name": "Luxury Apartments",
            "description": "High-end residential project",
            "type": "residential",
            "status": "in_progress",
            "location": "Downtown",
            "total_units": 100,
            "price_range": "50L-1Cr",
            "amenities": ["Pool", "Gym"],
            "created_at": "2024-03-20T10:00:00Z",
            "updated_at": "2024-03-20T10:00:00Z"
        }
    ],
    "total": 1,
    "page": 1,
    "limit": 10
}
```

### Create Project
```http
POST /api/v1/projects/
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "New Project",
    "description": "Project description",
    "type": "residential",
    "status": "planning",
    "location": "Location",
    "total_units": 50,
    "price_range": "30L-70L",
    "amenities": ["Parking", "Security"]
}
```

Response:
```json
{
    "id": 2,
    "name": "New Project",
    "description": "Project description",
    "type": "residential",
    "status": "planning",
    "location": "Location",
    "total_units": 50,
    "price_range": "30L-70L",
    "amenities": ["Parking", "Security"],
    "created_at": "2024-03-20T11:00:00Z",
    "updated_at": "2024-03-20T11:00:00Z"
}
```

### Get Project
```http
GET /api/v1/projects/{project_id}
Authorization: Bearer <token>
```

Response:
```json
{
    "id": 1,
    "name": "Luxury Apartments",
    "description": "High-end residential project",
    "type": "residential",
    "status": "in_progress",
    "location": "Downtown",
    "total_units": 100,
    "price_range": "50L-1Cr",
    "amenities": ["Pool", "Gym"],
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

### Update Project
```http
PUT /api/v1/projects/{project_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "Updated Project",
    "status": "in_progress"
}
```

Response:
```json
{
    "id": 1,
    "name": "Updated Project",
    "description": "High-end residential project",
    "type": "residential",
    "status": "in_progress",
    "location": "Downtown",
    "total_units": 100,
    "price_range": "50L-1Cr",
    "amenities": ["Pool", "Gym"],
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T11:00:00Z"
}
```

### Delete Project
```http
DELETE /api/v1/projects/{project_id}
Authorization: Bearer <token>
```

Response: 204 No Content

### Get Project Statistics
```http
GET /api/v1/projects/{project_id}/stats
Authorization: Bearer <token>
```

Response:
```json
{
    "total_leads": 50,
    "active_leads": 30,
    "converted_leads": 10,
    "conversion_rate": 20.0
}
```

### Get Project Analytics
```http
GET /api/v1/projects/{project_id}/analytics
Authorization: Bearer <token>
```

Query Parameters:
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

Response:
```json
{
    "lead_trends": [
        {
            "date": "2024-03-01",
            "count": 5
        }
    ],
    "status_distribution": [
        {
            "status": "new",
            "count": 20
        }
    ]
}
```

## Leads

### List Leads
```http
GET /api/v1/leads/
Authorization: Bearer <token>
```

Query Parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `status`: Filter by status
- `source`: Filter by source
- `search`: Search in name and email
- `date_range`: Filter by date range

Response:
```json
{
    "items": [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "status": "new",
            "source": "website",
            "notes": "Interested in 2BHK",
            "created_at": "2024-03-20T10:00:00Z",
            "updated_at": "2024-03-20T10:00:00Z"
        }
    ],
    "total": 1,
    "page": 1,
    "limit": 10
}
```

### Create Lead
```http
POST /api/v1/leads/
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "0987654321",
    "status": "new",
    "source": "website",
    "notes": "Interested in 3BHK"
}
```

Response:
```json
{
    "id": 2,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "0987654321",
    "status": "new",
    "source": "website",
    "notes": "Interested in 3BHK",
    "created_at": "2024-03-20T11:00:00Z",
    "updated_at": "2024-03-20T11:00:00Z"
}
```

### Get Lead
```http
GET /api/v1/leads/{lead_id}
Authorization: Bearer <token>
```

Response:
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "status": "new",
    "source": "website",
    "notes": "Interested in 2BHK",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

### Update Lead
```http
PUT /api/v1/leads/{lead_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "status": "contacted",
    "notes": "Called and scheduled site visit"
}
```

Response:
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "status": "contacted",
    "source": "website",
    "notes": "Called and scheduled site visit",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T11:00:00Z"
}
```

### Delete Lead
```http
DELETE /api/v1/leads/{lead_id}
Authorization: Bearer <token>
```

Response: 204 No Content

## Outreach

### Create Outreach
```http
POST /api/v1/outreach/leads/{lead_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "channel": "email",
    "message": "Thank you for your interest",
    "subject": "Welcome to Our Project",
    "template_id": "welcome_email"
}
```

Response:
```json
{
    "id": 1,
    "lead_id": 1,
    "channel": "email",
    "message": "Thank you for your interest",
    "subject": "Welcome to Our Project",
    "template_id": "welcome_email",
    "status": "sent",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

### List Outreach
```http
GET /api/v1/outreach/
Authorization: Bearer <token>
```

Query Parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `channel`: Filter by channel
- `status`: Filter by status
- `date_range`: Filter by date range

Response:
```json
{
    "items": [
        {
            "id": 1,
            "lead_id": 1,
            "channel": "email",
            "message": "Thank you for your interest",
            "subject": "Welcome to Our Project",
            "template_id": "welcome_email",
            "status": "sent",
            "created_at": "2024-03-20T10:00:00Z",
            "updated_at": "2024-03-20T10:00:00Z"
        }
    ],
    "total": 1,
    "page": 1,
    "limit": 10
}
```

### Get Lead Outreach
```http
GET /api/v1/outreach/leads/{lead_id}
Authorization: Bearer <token>
```

Response:
```json
[
    {
        "id": 1,
        "lead_id": 1,
        "channel": "email",
        "message": "Thank you for your interest",
        "subject": "Welcome to Our Project",
        "template_id": "welcome_email",
        "status": "sent",
        "created_at": "2024-03-20T10:00:00Z",
        "updated_at": "2024-03-20T10:00:00Z"
    }
]
```

### Get Outreach Statistics
```http
GET /api/v1/outreach/stats
Authorization: Bearer <token>
```

Query Parameters:
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

Response:
```json
{
    "total": 100,
    "successful": 80,
    "failed": 20,
    "scheduled": 10,
    "response_rate": 75.0,
    "average_response_time": 2.5
}
```

### Get Outreach Analytics
```http
GET /api/v1/outreach/analytics
Authorization: Bearer <token>
```

Query Parameters:
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

Response:
```json
{
    "trends": [
        {
            "date": "2024-03-01",
            "count": 10
        }
    ],
    "channel_stats": [
        {
            "channel": "email",
            "count": 50,
            "success_rate": 90.0
        }
    ],
    "response_time_distribution": [
        {
            "range": "0-1h",
            "count": 30
        }
    ],
    "status_distribution": [
        {
            "status": "sent",
            "count": 80
        }
    ]
}
```

### Schedule Outreach
```http
POST /api/v1/outreach/leads/{lead_id}/schedule
Authorization: Bearer <token>
Content-Type: application/json

{
    "channel": "email",
    "message": "Follow-up message",
    "subject": "Follow-up",
    "schedule_time": "2024-03-21T10:00:00Z"
}
```

Response:
```json
{
    "id": 2,
    "lead_id": 1,
    "channel": "email",
    "message": "Follow-up message",
    "subject": "Follow-up",
    "schedule_time": "2024-03-21T10:00:00Z",
    "status": "scheduled",
    "created_at": "2024-03-20T11:00:00Z",
    "updated_at": "2024-03-20T11:00:00Z"
}
```

### Cancel Scheduled Outreach
```http
DELETE /api/v1/outreach/leads/{lead_id}/schedule/{outreach_id}
Authorization: Bearer <token>
```

Response: 204 No Content

## Error Responses

### 400 Bad Request
```json
{
    "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
    "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
    "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
    "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "invalid email address",
            "type": "value_error.email"
        }
    ]
}
```

### 500 Internal Server Error
```json
{
    "detail": "Internal server error"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. The current limits are:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

When rate limit is exceeded, the API returns a 429 Too Many Requests response:
```json
{
    "detail": "Too many requests"
}
```

## Authentication

All endpoints except `/api/v1/auth/login` require authentication using a Bearer token. The token should be included in the Authorization header:

```http
Authorization: Bearer <token>
```

## Role-Based Access Control

The API implements role-based access control with the following roles:
- ADMIN: Full access to all endpoints
- MANAGER: Access to project and lead management
- AGENT: Access to lead management and outreach
- VIEWER: Read-only access to projects and leads

## Best Practices

1. Always include proper error handling in your requests
2. Use pagination for list endpoints to prevent large data transfers
3. Implement proper caching strategies for frequently accessed data
4. Use appropriate HTTP methods for different operations
5. Include proper validation for all input data
6. Implement proper logging and monitoring
7. Use HTTPS for all API calls
8. Keep authentication tokens secure
9. Implement proper rate limiting
10. Use appropriate HTTP status codes 