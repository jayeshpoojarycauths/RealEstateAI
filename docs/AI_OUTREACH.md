# AI Outreach Documentation

## Overview

The AI Outreach module provides automated communication capabilities across multiple channels, including email, SMS, WhatsApp, and Telegram. It uses a mock engine for testing and can be extended to integrate with real communication services.

## Features

### 1. Multi-channel Communication

#### Supported Channels
- Email
- SMS
- WhatsApp
- Telegram

#### Channel-specific Features
- Email: HTML templates, attachments
- SMS: Short message format, delivery status
- WhatsApp: Rich media, quick replies
- Telegram: Bot integration, inline keyboards

### 2. Communication Preferences

#### API Endpoint
```
PUT /api/v1/preferences
```

#### Configuration Options
```typescript
interface CommunicationPreference {
  default_channel: string;
  email_template?: string;
  sms_template?: string;
  whatsapp_template?: string;
  telegram_template?: string;
  working_hours_start?: string;
  working_hours_end?: string;
  max_daily_outreach?: number;
}
```

### 3. Outreach Engine

#### Mock Engine
The mock engine simulates communication channels for testing purposes.

```typescript
class MockOutreachEngine {
  constructor(preferences: CommunicationPreference);
  generate_message(lead: Lead): string;
  send(outreach: Outreach): OutreachResult;
}
```

#### Success Rates
- Email: 95%
- SMS: 90%
- WhatsApp: 85%
- Telegram: 80%

### 4. Message Templates

#### Template Variables
- {name}: Lead's name
- {project_name}: Project name
- {agent_name}: Agent's name

#### Channel-specific Templates
```typescript
const channel_templates = {
  email: {
    subject: 'Interested in {project_name}?',
    body: 'Hi {name},\n\nI noticed you were interested in {project_name}. Would you like to schedule a viewing?\n\nBest regards,\n{agent_name}'
  },
  sms: {
    body: 'Hi {name}, interested in {project_name}? Reply YES to schedule a viewing.'
  },
  whatsapp: {
    body: 'Hi {name}! 👋 I noticed you were interested in {project_name}. Would you like to schedule a viewing?'
  },
  telegram: {
    body: 'Hi {name}! I noticed you were interested in {project_name}. Would you like to schedule a viewing?'
  }
};
```

## Frontend Components

### 1. OutreachConfig Component

The `OutreachConfig` component provides a user interface for configuring communication preferences.

#### Features
- Channel selection
- Template configuration
- Working hours setup
- Daily limit setting

#### Usage
```tsx
import { OutreachConfig } from '@/components/outreach/OutreachConfig';

function SettingsPage() {
  return (
    <div>
      <h1>Outreach Settings</h1>
      <OutreachConfig />
    </div>
  );
}
```

### 2. Outreach Triggers

#### Single Lead Outreach
```typescript
POST /api/v1/outreach/leads/{lead_id}
```

#### Bulk Outreach
```typescript
POST /api/v1/outreach/leads/bulk-outreach
```

## Error Handling

### Common Errors
- Invalid channel configuration
- Template parsing errors
- Rate limiting
- Network failures

### Error Responses
```typescript
interface ErrorResponse {
  detail: string;
  code: string;
  status: number;
}
```

## Best Practices

1. **Template Management**
   - Use clear, concise language
   - Include call-to-action
   - Personalize messages
   - Test templates before use

2. **Channel Selection**
   - Consider lead preferences
   - Respect working hours
   - Monitor success rates
   - A/B test messages

3. **Performance**
   - Implement rate limiting
   - Use async processing
   - Cache templates
   - Monitor response times

4. **Security**
   - Validate templates
   - Sanitize user input
   - Secure API endpoints
   - Monitor usage

## Testing

### Unit Tests
- Template generation
- Channel selection
- Error handling
- Rate limiting

### Integration Tests
- API endpoints
- Database operations
- Frontend-backend integration
- Error scenarios

### E2E Tests
- Complete outreach flow
- Template configuration
- Error handling
- User interactions

## Future Enhancements

1. **AI Integration**
   - Smart template selection
   - Response analysis
   - Lead scoring
   - Automated follow-ups

2. **Analytics**
   - Channel performance
   - Response rates
   - Conversion tracking
   - ROI analysis

3. **Automation**
   - Scheduled outreach
   - Trigger-based messages
   - Workflow automation
   - Lead nurturing 