# Database Setup Instructions

## Setting up PostgreSQL Environment Variable

### PowerShell Commands
```powershell
# Set the DATABASE_URL environment variable
$env:DATABASE_URL="postgresql://postgres:secure_password@localhost/real_estate_crm"

# Verify the environment variable is set
$env:DATABASE_URL

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Permanent Setup (Windows)
1. Open System Properties (Win + Pause/Break)
2. Click on "Advanced system settings"
3. Click on "Environment Variables"
4. Under "User variables", click "New"
5. Set:
   - Variable name: `DATABASE_URL`
   - Variable value: `postgresql://postgres:secure_password@localhost/real_estate_crm`

## Default PostgreSQL Configuration
```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=real_estate_crm
```

## Troubleshooting

### Common Issues
1. If you see `%DATABASE_URL%` in the output, you're using CMD syntax in PowerShell. Use `$env:DATABASE_URL` instead.
2. If the application still uses SQLite, verify the environment variable is set correctly using `$env:DATABASE_URL`
3. Make sure PostgreSQL is running and accessible with the provided credentials

### Verifying Database Connection
```powershell
# Check if PostgreSQL is running
pg_isready -h localhost

# Connect to PostgreSQL
psql -h localhost -U postgres -d real_estate_crm
```

## Notes
- Replace `secure_password` with your actual PostgreSQL password
- The database name `real_estate_crm` should match your PostgreSQL database name
- Make sure PostgreSQL is installed and running on your system 