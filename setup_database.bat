@echo off
setlocal enabledelayedexpansion

:: === CONFIGURATION ===
set "DB_NAME=real_estate_crm"
set "DB_USER=postgres"
set "DB_PASSWORD=securepassword"
set "SCHEMA_FILE=schema.sql"
set "MOCK_DATA_FILE=mock_data.sql"
set "TRIGGERS_FILE=triggers.sql"

:: === CHECK FOR PSQL ===
where psql >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] PostgreSQL CLI tools not found in PATH.
    echo Make sure PostgreSQL is installed and added to PATH.
    exit /b 1
)

:: === CREATE DATABASE ===
echo.
echo [INFO] Creating database "%DB_NAME%"...
psql -U %DB_USER% -c "CREATE DATABASE %DB_NAME%;" 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Database might already exist. Continuing...
)

:: === CREATE USER ===
echo.
echo [INFO] Creating user "%DB_USER%"...
psql -U postgres -c "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '%DB_USER%') THEN CREATE ROLE %DB_USER% LOGIN PASSWORD '%DB_PASSWORD%'; END IF; END $$;"

:: === GRANT PRIVILEGES ===
echo [INFO] Granting privileges...
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"

:: === RUN SCHEMA ===
echo.
if not exist "%SCHEMA_FILE%" (
    echo [ERROR] Schema file "%SCHEMA_FILE%" not found!
    exit /b 1
)
echo [INFO] Running schema from "%SCHEMA_FILE%"...
psql -U %DB_USER% -d %DB_NAME% -f %SCHEMA_FILE%

:: === RUN MOCK DATA ===
echo.
if exist "%MOCK_DATA_FILE%" (
    echo [INFO] Inserting mock data from "%MOCK_DATA_FILE%"...
    psql -U %DB_USER% -d %DB_NAME% -f %MOCK_DATA_FILE%
) else (
    echo [INFO] No mock data file found. Skipping.
)

:: === RUN TRIGGERS ===
echo.
if exist "%TRIGGERS_FILE%" (
    echo [INFO] Applying triggers from "%TRIGGERS_FILE%"...
    psql -U %DB_USER% -d %DB_NAME% -f %TRIGGERS_FILE%
) else (
    echo [INFO] No triggers file found. Skipping.
)

:: === DONE ===
echo.
echo [SUCCESS] Database setup complete!
echo.
echo Login credentials:
echo   Admin   : admin@demo.com / password123
echo   Manager : manager@demo.com / password123
echo   Agent   : agent@demo.com / password123
echo.
pause
