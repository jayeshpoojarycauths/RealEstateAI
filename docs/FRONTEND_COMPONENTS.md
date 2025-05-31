 # Frontend Components Documentation

## Overview

The frontend is built using React with TypeScript, utilizing Ant Design for UI components and various other libraries for state management, routing, and data visualization.

## Core Components

### Authentication Components

#### AuthContext
- **Location**: `src/contexts/AuthContext.tsx`
- **Purpose**: Manages authentication state and user session
- **Key Features**:
  - JWT token management
  - User session persistence
  - Login/logout functionality
  - Role-based access control
- **Usage**:
```typescript
const { user, token, login, logout, isAuthenticated } = useAuth();
```

### Lead Management Components

#### LeadList
- **Location**: `src/components/leads/LeadList.tsx`
- **Purpose**: Displays and manages leads
- **Features**:
  - CRUD operations for leads
  - Filtering and search
  - Status management
  - Pagination
- **Props**:
  - `onLeadUpdate`: Callback for lead updates
  - `onLeadDelete`: Callback for lead deletion
- **Usage**:
```typescript
<LeadList onLeadUpdate={handleUpdate} onLeadDelete={handleDelete} />
```

### Project Management Components

#### ProjectList
- **Location**: `src/components/projects/ProjectList.tsx`
- **Purpose**: Displays and manages real estate projects
- **Features**:
  - Project listing with filters
  - Project creation and editing
  - Project statistics
  - Analytics visualization
- **Props**:
  - `onProjectUpdate`: Callback for project updates
  - `onProjectDelete`: Callback for project deletion
- **Usage**:
```typescript
<ProjectList onProjectUpdate={handleUpdate} onProjectDelete={handleDelete} />
```

### Outreach Components

#### OutreachList
- **Location**: `src/components/outreach/OutreachList.tsx`
- **Purpose**: Manages communication with leads
- **Features**:
  - Multi-channel communication
  - Message scheduling
  - Template management
  - Analytics dashboard
- **Props**:
  - `leadId`: ID of the lead
  - `onOutreachComplete`: Callback for outreach completion
- **Usage**:
```typescript
<OutreachList leadId={1} onOutreachComplete={handleComplete} />
```

## Common Components

### Layout Components

#### Header
- **Location**: `src/components/common/Header.tsx`
- **Purpose**: Main navigation header
- **Features**:
  - User profile
  - Navigation menu
  - Search functionality
- **Props**:
  - `user`: Current user information
  - `onLogout`: Logout callback

#### Sidebar
- **Location**: `src/components/common/Sidebar.tsx`
- **Purpose**: Main navigation sidebar
- **Features**:
  - Navigation links
  - Collapsible menu
  - Role-based menu items
- **Props**:
  - `collapsed`: Sidebar collapse state
  - `onCollapse`: Collapse callback

### Form Components

#### ProjectForm
- **Location**: `src/components/projects/ProjectForm.tsx`
- **Purpose**: Project creation and editing form
- **Features**:
  - Form validation
  - File upload
  - Rich text editing
- **Props**:
  - `initialValues`: Initial form values
  - `onSubmit`: Form submission callback

#### LeadForm
- **Location**: `src/components/leads/LeadForm.tsx`
- **Purpose**: Lead creation and editing form
- **Features**:
  - Contact information
  - Status management
  - Notes and comments
- **Props**:
  - `initialValues`: Initial form values
  - `onSubmit`: Form submission callback

## State Management

### API Service
- **Location**: `src/services/api.ts`
- **Purpose**: Centralized API communication
- **Features**:
  - Axios instance configuration
  - Request/response interceptors
  - Error handling
  - Authentication header management

### Auth Store
- **Location**: `src/stores/authStore.ts`
- **Purpose**: Authentication state management
- **Features**:
  - User session management
  - Token storage
  - Role-based permissions

## Utility Functions

### Formatters
- **Location**: `src/utils/formatters.ts`
- **Purpose**: Data formatting utilities
- **Features**:
  - Date formatting
  - Currency formatting
  - Phone number formatting

### Validators
- **Location**: `src/utils/validators.ts`
- **Purpose**: Form validation utilities
- **Features**:
  - Email validation
  - Phone number validation
  - Required field validation

## Best Practices

1. **Component Organization**
   - Keep components small and focused
   - Use composition over inheritance
   - Implement proper prop types

2. **State Management**
   - Use React Context for global state
   - Implement proper loading states
   - Handle errors gracefully

3. **Performance**
   - Implement proper memoization
   - Use pagination for large lists
   - Optimize re-renders

4. **Type Safety**
   - Use TypeScript interfaces
   - Implement proper type checking
   - Use enums for constants

5. **Testing**
   - Write unit tests for components
   - Test user interactions
   - Mock API calls

## Development Guidelines

1. **Code Style**
   - Follow TypeScript best practices
   - Use ESLint for code quality
   - Implement proper error handling

2. **Component Structure**
   - Use functional components
   - Implement proper hooks
   - Follow React best practices

3. **API Integration**
   - Use proper error handling
   - Implement loading states
   - Handle edge cases

4. **Testing**
   - Write comprehensive tests
   - Use testing-library
   - Mock external dependencies