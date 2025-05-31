#!/bin/bash

# Database configuration
DB_NAME="real_estate_crm"
DB_USER="postgres"
DB_PASSWORD="your_password_here"  # Change this to your desired password

# Create database
echo "Creating database..."
psql -U postgres -c "CREATE DATABASE $DB_NAME;"

# Create user and grant privileges
echo "Creating user and granting privileges..."
psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Connect to the database and run schema
echo "Running schema..."
psql -U $DB_USER -d $DB_NAME -f schema.sql

# Run mock data
echo "Inserting mock data..."
psql -U $DB_USER -d $DB_NAME -f mock_data.sql

echo "Database setup complete!" 