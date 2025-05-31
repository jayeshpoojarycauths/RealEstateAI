from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.models import Project, ProjectLead, Lead, Customer
from app.project.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectFilter,
    ProjectStats, ProjectAnalytics
)
from app.core.pagination import PaginationParams

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    async def get_projects(
        self,
        customer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """Get all projects for a customer."""
        return self.db.query(Project).filter(
            Project.customer_id == customer_id
        ).offset(skip).limit(limit).all()

    async def get_project(self, project_id: int, customer_id: int) -> Optional[Project]:
        """Get a specific project."""
        return self.db.query(Project).filter(
            Project.id == project_id,
            Project.customer_id == customer_id
        ).first()

    async def create_project(
        self,
        project_in: ProjectCreate,
        customer_id: int
    ) -> Project:
        """Create a new project."""
        project = Project(
            **project_in.dict(),
            customer_id=customer_id
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    async def update_project(
        self,
        project_id: int,
        project_in: ProjectUpdate,
        customer_id: int
    ) -> Optional[Project]:
        """Update a project."""
        project = await self.get_project(project_id, customer_id)
        if not project:
            return None

        for field, value in project_in.dict(exclude_unset=True).items():
            setattr(project, field, value)

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    async def delete_project(self, project_id: int, customer_id: int) -> bool:
        """Delete a project."""
        project = await self.get_project(project_id, customer_id)
        if not project:
            return False

        self.db.delete(project)
        self.db.commit()
        return True

    async def get_project_stats(self, customer_id: int) -> ProjectStats:
        """Get project statistics for a customer."""
        total_projects = self.db.query(func.count(Project.id)).filter(
            Project.customer_id == customer_id
        ).scalar()

        active_projects = self.db.query(func.count(Project.id)).filter(
            Project.customer_id == customer_id,
            Project.status == "active"
        ).scalar()

        completed_projects = self.db.query(func.count(Project.id)).filter(
            Project.customer_id == customer_id,
            Project.status == "completed"
        ).scalar()

        budget_stats = self.db.query(
            func.sum(Project.budget).label("total_budget"),
            func.avg(Project.budget).label("average_budget")
        ).filter(
            Project.customer_id == customer_id,
            Project.budget.isnot(None)
        ).first()

        return ProjectStats(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            total_budget=budget_stats.total_budget or 0.0,
            average_budget=budget_stats.average_budget or 0.0
        )

    async def get_project_analytics(self, customer_id: int) -> ProjectAnalytics:
        """Get project analytics for a customer."""
        # Projects by status
        status_counts = self.db.query(
            Project.status,
            func.count(Project.id)
        ).filter(
            Project.customer_id == customer_id
        ).group_by(Project.status).all()
        projects_by_status = dict(status_counts)

        # Projects by month
        month_counts = self.db.query(
            func.date_trunc('month', Project.created_at).label('month'),
            func.count(Project.id)
        ).filter(
            Project.customer_id == customer_id
        ).group_by('month').all()
        projects_by_month = {str(month): count for month, count in month_counts}

        # Budget distribution
        budget_ranges = self.db.query(
            func.width_bucket(Project.budget, 0, 1000000, 10).label('range'),
            func.count(Project.id)
        ).filter(
            Project.customer_id == customer_id,
            Project.budget.isnot(None)
        ).group_by('range').all()
        budget_distribution = {f"range_{r}": c for r, c in budget_ranges}

        return ProjectAnalytics(
            projects_by_status=projects_by_status,
            projects_by_month=projects_by_month,
            budget_distribution=budget_distribution
        )

    async def assign_lead(self, project_id: int, lead_id: int, customer_id: int) -> bool:
        """
        Assign a lead to a project.
        """
        project = await self.get_project(project_id, customer_id)
        if not project:
            return False

        lead = self.db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.customer_id == customer_id
        ).first()
        if not lead:
            return False

        # Check if lead is already assigned
        existing = self.db.query(ProjectLead).filter(
            ProjectLead.project_id == project_id,
            ProjectLead.lead_id == lead_id
        ).first()
        if existing:
            return True

        # Assign lead
        project_lead = ProjectLead(project_id=project_id, lead_id=lead_id)
        self.db.add(project_lead)
        self.db.commit()
        return True

    async def remove_lead(self, project_id: int, lead_id: int, customer_id: int) -> bool:
        """
        Remove a lead from a project.
        """
        project = await self.get_project(project_id, customer_id)
        if not project:
            return False

        lead = self.db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.customer_id == customer_id
        ).first()
        if not lead:
            return False

        # Remove lead
        self.db.query(ProjectLead).filter(
            ProjectLead.project_id == project_id,
            ProjectLead.lead_id == lead_id
        ).delete()
        self.db.commit()
        return True 