from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.shared.core.config import settings
from app.shared.core.middleware import rate_limit_middleware
from app.api.v1.api import api_router
from app.shared.core.security import get_current_customer
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from app.tasks.reporting import (
    generate_daily_reports,
    generate_weekly_reports,
    generate_monthly_reports,
    generate_quarterly_reports,
    cleanup_old_reports
)
from app.models.models import CommunicationPreferences, User, Customer, Lead, Project, ProjectLead, AuditLog, OutreachLog, InteractionLog, CommunicationChannel

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this based on your environment
)

# Set all CORS enabled origins
# if settings.BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting middleware
app.add_middleware(rate_limit_middleware)

# app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router, prefix="/api/v1")

# Set up scheduler for automated tasks
scheduler = BackgroundScheduler()

# Schedule daily report generation at 1 AM
scheduler.add_job(
    generate_daily_reports,
    'cron',
    hour=1,
    minute=0
)

# Schedule weekly report generation on Monday at 2 AM
scheduler.add_job(
    generate_weekly_reports,
    'cron',
    day_of_week='mon',
    hour=2,
    minute=0
)

# Schedule monthly report generation on the 1st of each month at 3 AM
scheduler.add_job(
    generate_monthly_reports,
    'cron',
    day=1,
    hour=3,
    minute=0
)

# Schedule quarterly report generation on the 1st of each quarter at 4 AM
scheduler.add_job(
    generate_quarterly_reports,
    'cron',
    month='1,4,7,10',
    day=1,
    hour=4,
    minute=0
)

# Schedule cleanup of old reports at 5 AM daily
scheduler.add_job(
    cleanup_old_reports,
    'cron',
    hour=5,
    minute=0
)

# OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Dependency for getting current customer
app.dependency_overrides[get_current_customer] = get_current_customer

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

@app.get("/")
def root():
    return {"message": "Welcome to Real Estate CRM API"} 