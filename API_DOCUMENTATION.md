 # Real Estate CRM API Documentation

## Table of Contents
1. [Project Management Endpoints](#project-management-endpoints)
2. [Outreach Management Endpoints](#outreach-management-endpoints)
3. [Lead Management Endpoints](#lead-management-endpoints)

## Project Management Endpoints

### List Projects
```http
GET /api/v1/projects/
```

Lists all projects with pagination and filtering options.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `status`: Filter by project status (planning, in_progress, completed, on_hold, cancelled)
- `type`: Filter by project type (residential, commercial, land, rental)
- `search`: Search in project name and description

**Response:**
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
            "customer_id": 1,
            "created_at": "2024-03-15T10:00:00",
            "updated_at": "2024-03-15T10:00:00"
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
```

Creates a new real estate project.

**Request Body:**
```json
{
    "name": "Luxury Apartments",
    "description": "High-end residential project",
    "type": "residential",
    "status": "planning",
    "location": "Downtown",
    "total_units": 100,
    "price_range": "50L-1Cr",
    "amenities": ["Pool", "Gym"],
    "completion_date": "2025-12-31T00:00:00"
}
```

**Response:** Returns the created project object.

### Get Project
```http
GET /api/v1/projects/{project_id}
```

Retrieves a specific project by ID.

**Response:** Returns the project object.

### Update Project
```http
PUT /api/v1/projects/{project_id}
```

Updates an existing project.

**Request Body:**
```json
{
    "name": "Updated Project Name",
    "status": "in_progress",
    "price_range": "60L-1.2Cr"
}
```

**Response:** Returns the updated project object.

### Delete Project
```http
DELETE /api/v1/projects/{project_id}
```

Deletes a project.

**Response:**
```json
{
    "message": "Project deleted successfully"
}
```

### Get Project Statistics
```http
GET /api/v1/projects/{project_id}/stats
```

Retrieves statistics for a specific project.

**Response:**
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
```

Retrieves analytics data for a project with date range filtering.

**Query Parameters:**
- `start_date`: Start date for analytics (YYYY-MM-DD)
- `end_date`: End date for analytics (YYYY-MM-DD)

**Response:**
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
            "status": "active",
            "count": 30
        }
    ]
}
```

### Assign Lead to Project
```http
POST /api/v1/projects/{project_id}/leads/{lead_id}
```

Assigns a lead to a project.

**Response:**
```json
{
    "message": "Lead assigned successfully"
}
```

### Remove Lead from Project
```http
DELETE /api/v1/projects/{project_id}/leads/{lead_id}
```

Removes a lead from a project.

**Response:**
```json
{
    "message": "Lead removed successfully"
}
```

## Outreach Management Endpoints

### Create Outreach
```http
POST /api/v1/outreach/leads/{lead_id}
```

Creates a new outreach to a lead.

**Request Body:**
```json
{
    "channel": "email",
    "message": "Hello, we have a new property that matches your requirements.",
    "subject": "New Property Alert",
    "template_id": "template_123",
    "variables": {
        "name": "John Doe",
        "property_name": "Luxury Villa"
    }
}
```

**Response:** Returns the created outreach object.

### List Outreach
```http
GET /api/v1/outreach/
```

Lists all outreach attempts with pagination and filtering.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `channel`: Filter by channel (email, sms, call, whatsapp)
- `status`: Filter by status (scheduled, sent, delivered, read, failed, cancelled)
- `start_date`: Filter by start date (YYYY-MM-DD)
- `end_date`: Filter by end date (YYYY-MM-DD)
- `search`: Search in message content

**Response:** Returns a paginated list of outreach attempts.

### Get Lead Outreach
```http
GET /api/v1/outreach/leads/{lead_id}
```

Gets all outreach attempts for a specific lead.

**Response:** Returns a list of outreach attempts for the lead.

### Get Outreach Statistics
```http
GET /api/v1/outreach/stats
```

Gets outreach statistics with date range filtering.

**Query Parameters:**
- `start_date`: Start date for statistics (YYYY-MM-DD)
- `end_date`: End date for statistics (YYYY-MM-DD)

**Response:**
```json
{
    "total_outreach": 100,
    "successful_outreach": 80,
    "failed_outreach": 20,
    "scheduled_outreach": 10,
    "response_rate": 75.5,
    "average_response_time": 2.5
}
```

### Get Outreach Analytics
```http
GET /api/v1/outreach/analytics
```

Gets detailed outreach analytics with date range filtering.

**Query Parameters:**
- `start_date`: Start date for analytics (YYYY-MM-DD)
- `end_date`: End date for analytics (YYYY-MM-DD)

**Response:**
```json
{
    "trends": [
        {
            "date": "2024-03-01",
            "count": 10,
            "channel": "email"
        }
    ],
    "channel_stats": [
        {
            "channel": "email",
            "total": 50,
            "successful": 45,
            "failed": 5,
            "response_rate": 90.0
        }
    ],
    "response_time_distribution": [
        {
            "range": "0-1h",
            "count": 20
        }
    ],
    "status_distribution": [
        {
            "status": "delivered",
            "count": 80
        }
    ]
}
```

### Schedule Outreach
```http
POST /api/v1/outreach/leads/{lead_id}/schedule
```

Schedules an outreach to a lead for a specific time.

**Request Body:**
```json
{
    "channel": "email",
    "message": "Reminder: Property viewing tomorrow at 2 PM",
    "subject": "Viewing Reminder",
    "schedule_time": "2024-03-20 14:00:00"
}
```

**Response:** Returns the scheduled outreach object.

### Cancel Scheduled Outreach
```http
DELETE /api/v1/outreach/leads/{lead_id}/schedule/{outreach_id}
```

Cancels a scheduled outreach.

**Response:**
```json
{
    "message": "Scheduled outreach cancelled successfully"
}
```

## Lead Management Endpoints

### List Leads
```http
GET /api/v1/leads/
```

Lists all leads with pagination and filtering.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `status`: Filter by lead status
- `source`: Filter by lead source
- `search`: Search in lead name, email, or phone

**Response:** Returns a paginated list of leads.

### Create Lead
```http
POST /api/v1/leads/
```

Creates a new lead.

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "source": "website",
    "status": "new",
    "notes": "Interested in 3BHK apartment"
}
```

**Response:** Returns the created lead object.

### Get Lead
```http
GET /api/v1/leads/{lead_id}
```

Retrieves a specific lead by ID.

**Response:** Returns the lead object.

### Update Lead
```http
PUT /api/v1/leads/{lead_id}
```

Updates an existing lead.

**Request Body:**
```json
{
    "status": "contacted",
    "notes": "Scheduled for site visit"
}
```

**Response:** Returns the updated lead object.

### Delete Lead
```http
DELETE /api/v1/leads/{lead_id}
```

Deletes a lead.

**Response:**
```json
{
    "message": "Lead deleted successfully"
}
```

### Upload Leads
```http
POST /api/v1/leads/upload
```

Uploads multiple leads from a CSV file.

**Request Body:**
- `file`: CSV file containing lead data

**Response:**
```json
{
    "message": "Leads uploaded successfully",
    "total_leads": 50,
    "successful": 48,
    "failed": 2
}
```

## Authentication

All endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

## Error Responses

The API uses standard HTTP status codes and returns error messages in the following format:

```json
{
    "detail": "Error message description"
}
```

Common status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error