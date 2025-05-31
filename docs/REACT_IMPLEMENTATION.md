# React Implementation Guide

## Required Packages

```json
{
  "dependencies": {
    "@ant-design/icons": "^5.0.0",
    "@ant-design/pro-components": "^2.4.4",
    "antd": "^5.0.0",
    "axios": "^1.3.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.1",
    "recharts": "^2.4.3",
    "zustand": "^4.3.6"
  },
  "devDependencies": {
    "@types/react": "^18.0.27",
    "@types/react-dom": "^18.0.10",
    "@typescript-eslint/eslint-plugin": "^5.45.0",
    "@typescript-eslint/parser": "^5.45.0",
    "typescript": "^4.9.4",
    "vite": "^4.0.4"
  }
}
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   ├── projects/
│   │   │   ├── ProjectList.tsx
│   │   │   ├── ProjectForm.tsx
│   │   │   └── ProjectAnalytics.tsx
│   │   ├── leads/
│   │   │   ├── LeadList.tsx
│   │   │   ├── LeadForm.tsx
│   │   │   └── LeadDetails.tsx
│   │   └── outreach/
│   │       ├── OutreachList.tsx
│   │       ├── OutreachForm.tsx
│   │       └── OutreachAnalytics.tsx
│   ├── contexts/
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   └── useApi.ts
│   ├── services/
│   │   ├── api.ts
│   │   └── auth.ts
│   ├── types/
│   │   ├── project.ts
│   │   ├── lead.ts
│   │   └── outreach.ts
│   └── utils/
│       ├── formatters.ts
│       └── validators.ts
```

## Setup Instructions

1. Create a new React project using Vite:
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
Create a `.env` file:
```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Real Estate CRM
```

4. Start the development server:
```bash
npm run dev
```

## Component Implementation

### Authentication

The application uses JWT tokens for authentication. The `AuthContext` provides authentication state and methods:

```typescript
// src/contexts/AuthContext.tsx
import { createContext, useContext, useState } from 'react';

interface AuthContextType {
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('token', newToken);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### API Integration

Create an API service using Axios:

```typescript
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Form Handling

Use Ant Design's Form component with TypeScript:

```typescript
// src/components/projects/ProjectForm.tsx
import { Form, Input, Select } from 'antd';
import { ProjectType, ProjectStatus } from '../../types/project';

interface ProjectFormProps {
  initialValues?: any;
  onSubmit: (values: any) => void;
}

const ProjectForm: React.FC<ProjectFormProps> = ({ initialValues, onSubmit }) => {
  const [form] = Form.useForm();

  return (
    <Form
      form={form}
      initialValues={initialValues}
      onFinish={onSubmit}
      layout="vertical"
    >
      {/* Form fields */}
    </Form>
  );
};
```

## Best Practices

1. **Type Safety**
   - Use TypeScript for all components and functions
   - Define interfaces for all props and state
   - Use enums for constants

2. **State Management**
   - Use React Context for global state
   - Use local state for component-specific state
   - Consider Zustand for complex state management

3. **API Calls**
   - Use Axios interceptors for authentication
   - Implement error handling
   - Use TypeScript for API responses

4. **Component Structure**
   - Keep components small and focused
   - Use composition over inheritance
   - Implement proper prop types

5. **Performance**
   - Use React.memo for expensive components
   - Implement proper loading states
   - Use pagination for large data sets

## Testing

1. Install testing dependencies:
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

2. Create test files:
```typescript
// src/components/projects/__tests__/ProjectList.test.tsx
import { render, screen } from '@testing-library/react';
import ProjectList from '../ProjectList';

describe('ProjectList', () => {
  it('renders project list', () => {
    render(<ProjectList />);
    expect(screen.getByText('Projects')).toBeInTheDocument();
  });
});
```

## Deployment

1. Build the project:
```bash
npm run build
```

2. Deploy to a static hosting service (e.g., Vercel, Netlify)

3. Configure environment variables in the hosting platform

## Additional Resources

- [Ant Design Documentation](https://ant.design/docs/react/introduce)
- [React Router Documentation](https://reactrouter.com/docs/en/v6)
- [Recharts Documentation](https://recharts.org/en-US/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/) 