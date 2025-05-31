# API Documentation

## Base URL
All API endpoints are prefixed with `/api/v1/`

## Authentication
All endpoints require authentication using a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Stats
- `GET /stats/price-trends/`
  - Query parameters:
    - `start_date` (optional): Start date in ISO format
    - `end_date` (optional): End date in ISO format
    - `location` (optional): Filter by location
    - `property_type` (optional): Filter by property type

- `GET /stats/lead-quality/`
  - Query parameters:
    - `start_date` (optional): Start date in ISO format
    - `end_date` (optional): End date in ISO format

- `GET /stats/lead-score/`
  - Returns distribution of leads by score buckets

- `GET /stats/conversion-funnel/`
  - Returns lead conversion funnel data

### Communication
- `GET /communication/preferences/`
  - Get communication preferences for current customer

- `POST /communication/preferences/`
  - Create communication preferences
  - Request body: `CommunicationPreferencesCreate`

- `PUT /communication/preferences/`
  - Update communication preferences
  - Request body: `CommunicationPreferencesUpdate`

- `POST /communication/send/{lead_id}/`
  - Send message to a lead
  - Path parameters:
    - `lead_id`: UUID of the lead
  - Request body:
    - `message`: Message content
    - `channel`: Communication channel (sms, email, whatsapp, telegram, voice)

- `POST /communication/send-bulk/`
  - Send message to multiple leads
  - Request body:
    - `lead_ids`: Array of lead UUIDs
    - `message`: Message content
    - `channel`: Communication channel

### Audit
- `GET /audit/logs/`
  - Get audit logs with filtering
  - Query parameters:
    - `resource_type` (optional): Filter by resource type
    - `resource_id` (optional): Filter by resource ID
    - `action` (optional): Filter by action
    - `start_date` (optional): Filter by start date
    - `end_date` (optional): Filter by end date
    - `user_id` (optional): Filter by user ID
    - `skip` (optional): Number of records to skip
    - `limit` (optional): Maximum number of records to return

## Data Types

### UUID Fields
All ID fields in the API use UUID format. This includes:
- Lead IDs
- Customer IDs
- User IDs
- Resource IDs
- Communication preference IDs
- Audit log IDs

### Communication Channels
Available communication channels:
- `sms`: SMS messages
- `email`: Email messages
- `whatsapp`: WhatsApp messages
- `telegram`: Telegram messages
- `voice`: Voice calls

## Error Responses
All error responses follow this format:
```json
{
  "detail": "Error message"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error 