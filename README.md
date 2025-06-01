# Real Estate AI Platform

A modern real estate platform with AI-powered features, role-based access control, and comprehensive property management.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+ and pip
- PostgreSQL 13+
- Redis (for background jobs)

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env` file:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

### Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize database:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

## 🔐 Role-Based Access Control

### Role Hierarchy

The platform implements a hierarchical role system:

- **Admin**: Full system access
  - Can manage all properties
  - Can view audit logs
  - Can manage users
  - Can access all features

- **Agent**: Property management access
  - Can manage assigned properties
  - Can view property analytics
  - Can communicate with customers

- **Customer**: Limited access
  - Can view available properties
  - Can save favorites
  - Can contact agents

### Permission Inheritance

Higher roles inherit permissions from lower roles:
```
Admin > Agent > Customer
```

## 🧪 Testing

### Unit Tests

Run frontend unit tests:
```bash
cd frontend
npm test
```

Run backend unit tests:
```bash
cd backend
pytest
```

### E2E Tests

Run Cypress tests:
```bash
cd frontend
npm run cypress:open
```

## 📦 Mock Data

### Frontend Fixtures

Mock data is available in `frontend/src/mocks/`:
- `properties.ts`: Sample property listings
- `users.ts`: User profiles with different roles
- `auditLogs.ts`: System activity logs

### Backend Seeds

Initialize test data:
```bash
cd backend
python scripts/seed_data.py
```

## 🔒 Security Features

1. **Token Management**
   - JWT-based authentication
   - Automatic token refresh
   - Token expiration handling

2. **Request Protection**
   - Request signing for critical actions
   - Nonce-based replay protection
   - Rate limiting

3. **Audit Logging**
   - Comprehensive activity tracking
   - IP address logging
   - User action history

## 🛠️ Development Guidelines

### Code Style

- Frontend: ESLint + Prettier
  ```bash
  npm run lint
  npm run format
  ```

- Backend: Black + isort
  ```bash
  black .
  isort .
  ```

### Git Workflow

1. Create feature branch
2. Write tests
3. Implement feature
4. Run tests
5. Create pull request

### API Documentation

- OpenAPI docs available at `/docs`
- Swagger UI at `/swagger`
- ReDoc at `/redoc`

## 📚 Additional Resources

- [Material Tailwind Documentation](https://material-tailwind.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Query Documentation](https://tanstack.com/query/latest)
- [Cypress Documentation](https://docs.cypress.io/)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 