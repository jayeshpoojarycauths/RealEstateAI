from fastapi import APIRouter

from app.analytics.api.v1.endpoints import analytics
from app.auth.api.v1.endpoints import auth
from app.lead.api.v1.endpoints import leads
from app.outreach.api.v1.endpoints import outreach
from app.project.api.v1.endpoints import projects
from app.scraping.api.v1.endpoints import scraping

# Create main API router
api_router = APIRouter()

# Include all feature routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(scraping.router, prefix="/scraping", tags=["scraping"])
api_router.include_router(outreach.router, prefix="/outreach", tags=["outreach"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"]) 