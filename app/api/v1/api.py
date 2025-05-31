from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    projects,
    leads,
    stats,
    analytics,
    communication,
    config,
    reports
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(communication.router, prefix="/communication", tags=["communication"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"]) 