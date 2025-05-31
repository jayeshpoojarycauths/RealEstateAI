# Data Models and Schemas Documentation

## Overview

This document outlines the data models and schemas used throughout the Real Estate CRM application. All models are implemented using TypeScript interfaces and enums for type safety.

## Core Models

### User Model

```typescript
enum UserRole {
    ADMIN = "admin",
    MANAGER = "manager",
    AGENT = "agent",
    VIEWER = "viewer"
}

interface User {
    id: number;
    email: string;
    roles: UserRole[];
    created_at: string;
    updated_at: string;
}
```

### Project Model

```typescript
enum ProjectType {
    RESIDENTIAL = "residential",
    COMMERCIAL = "commercial",
    MIXED_USE = "mixed_use"
}

enum ProjectStatus {
    PLANNING = "planning",
    IN_PROGRESS = "in_progress",
    COMPLETED = "completed",
    ON_HOLD = "on_hold"
}

interface Project {
    id: number;
    name: string;
    description: string;
    type: ProjectType;
    status: ProjectStatus;
    location: string;
    total_units: number;
    price_range: string;
    amenities: string[];
    created_at: string;
    updated_at: string;
}

interface ProjectStats {
    total_leads: number;
    active_leads: number;
    converted_leads: number;
    conversion_rate: number;
}

interface ProjectAnalytics {
    lead_trends: {
        date: string;
        count: number;
    }[];
    status_distribution: {
        status: string;
        count: number;
    }[];
}
```

### Lead Model

```typescript
enum LeadStatus {
    NEW = "new",
    CONTACTED = "contacted",
    QUALIFIED = "qualified",
    CONVERTED = "converted",
    LOST = "lost"
}

enum LeadSource {
    WEBSITE = "website",
    REFERRAL = "referral",
    SOCIAL_MEDIA = "social_media",
    DIRECT = "direct"
}

interface Lead {
    id: number;
    name: string;
    email: string;
    phone: string;
    status: LeadStatus;
    source: LeadSource;
    notes: string;
    assigned_to?: number;
    created_at: string;
    updated_at: string;
}

interface LeadStats {
    total_leads: number;
    new_leads: number;
    contacted_leads: number;
    qualified_leads: number;
    converted_leads: number;
    conversion_rate: number;
}

interface LeadAnalytics {
    lead_trends: {
        date: string;
        count: number;
    }[];
    source_distribution: {
        source: string;
        count: number;
    }[];
}
```

### Outreach Model

```typescript
enum OutreachChannel {
    EMAIL = "email",
    SMS = "sms",
    WHATSAPP = "whatsapp"
}

enum OutreachStatus {
    SCHEDULED = "scheduled",
    SENT = "sent",
    FAILED = "failed",
    DELIVERED = "delivered",
    READ = "read"
}

interface Outreach {
    id: number;
    lead_id: number;
    channel: OutreachChannel;
    message: string;
    subject?: string;
    template_id?: string;
    status: OutreachStatus;
    schedule_time?: string;
    created_at: string;
    updated_at: string;
}

interface OutreachStats {
    total: number;
    successful: number;
    failed: number;
    scheduled: number;
    response_rate: number;
    average_response_time: number;
}

interface OutreachAnalytics {
    trends: {
        date: string;
        count: number;
    }[];
    channel_stats: {
        channel: string;
        count: number;
        success_rate: number;
    }[];
    response_time_distribution: {
        range: string;
        count: number;
    }[];
    status_distribution: {
        status: string;
        count: number;
    }[];
}
```

## Request/Response Models

### Authentication

```typescript
interface LoginRequest {
    email: string;
    password: string;
}

interface LoginResponse {
    access_token: string;
    token_type: string;
    user: User;
}
```

### Project Management

```typescript
interface CreateProjectRequest {
    name: string;
    description: string;
    type: ProjectType;
    status: ProjectStatus;
    location: string;
    total_units: number;
    price_range: string;
    amenities: string[];
}

interface UpdateProjectRequest {
    name?: string;
    description?: string;
    type?: ProjectType;
    status?: ProjectStatus;
    location?: string;
    total_units?: number;
    price_range?: string;
    amenities?: string[];
}

interface ProjectListResponse {
    items: Project[];
    total: number;
    page: number;
    limit: number;
}
```

### Lead Management

```typescript
interface CreateLeadRequest {
    name: string;
    email: string;
    phone: string;
    status: LeadStatus;
    source: LeadSource;
    notes?: string;
    assigned_to?: number;
}

interface UpdateLeadRequest {
    name?: string;
    email?: string;
    phone?: string;
    status?: LeadStatus;
    source?: LeadSource;
    notes?: string;
    assigned_to?: number;
}

interface LeadListResponse {
    items: Lead[];
    total: number;
    page: number;
    limit: number;
}
```

### Outreach Management

```typescript
interface CreateOutreachRequest {
    channel: OutreachChannel;
    message: string;
    subject?: string;
    template_id?: string;
}

interface ScheduleOutreachRequest extends CreateOutreachRequest {
    schedule_time: string;
}

interface OutreachListResponse {
    items: Outreach[];
    total: number;
    page: number;
    limit: number;
}
```

## Filter Models

### Project Filters

```typescript
interface ProjectFilter {
    page?: number;
    limit?: number;
    status?: ProjectStatus;
    type?: ProjectType;
    search?: string;
}
```

### Lead Filters

```typescript
interface LeadFilter {
    page?: number;
    limit?: number;
    status?: LeadStatus;
    source?: LeadSource;
    search?: string;
    date_range?: [string, string];
}
```

### Outreach Filters

```typescript
interface OutreachFilter {
    page?: number;
    limit?: number;
    channel?: OutreachChannel;
    status?: OutreachStatus;
    date_range?: [string, string];
}
```

## Error Models

```typescript
interface ValidationError {
    loc: string[];
    msg: string;
    type: string;
}

interface ErrorResponse {
    detail: string | ValidationError[];
}
```

## Best Practices

1. **Type Safety**
   - Use TypeScript interfaces for all models
   - Implement proper validation
   - Use enums for constants

2. **Data Validation**
   - Validate all input data
   - Handle edge cases
   - Implement proper error handling

3. **API Integration**
   - Use proper request/response models
   - Implement proper error handling
   - Handle edge cases

4. **Documentation**
   - Document all models
   - Include examples
   - Update documentation regularly 