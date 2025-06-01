from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
import json

from app.project.models.project import (
    Project, ProjectLead, ProjectFeature,
    ProjectImage, ProjectAmenity, ProjectType,
    ProjectStatus
)
from app.project.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectFilter,
    ProjectStats, ProjectAnalytics, ProjectFeatureCreate,
    ProjectImageCreate, ProjectAmenityCreate, ProjectLeadCreate
)
from app.shared.core.exceptions import ValidationError, NotFoundError
from app.shared.core.audit import AuditService
from app.core.pagination import PaginationParams

class ProjectService:
    def __init__(self, db: Session):
    async def list_projects(
        self,
        customer_id: str,
        filter_params: ProjectFilter,
        pagination: PaginationParams
    ) -> tuple[List[Project], int]:
         """Get all projects for a customer with filtering."""
         query = self.db.query(Project).filter(Project.customer_id == customer_id)
         
         # Apply filters
         if filter_params.type:
             query = query.filter(Project.type == filter_params.type)
         # ... other filters ...
         
        # Get total count before pagination
        total_count = query.count()
        
         # Apply pagination
         query = query.offset(pagination.offset).limit(pagination.limit)
         
        return query.all(), total_count
            query = query.filter(Project.city.ilike(f"%{filter_params.city}%"))
        if filter_params.state:
            query = query.filter(Project.state.ilike(f"%{filter_params.state}%"))
        if filter_params.min_price:
            query = query.filter(Project.total_value >= filter_params.min_price)
        if filter_params.max_price:
            query = query.filter(Project.total_value <= filter_params.max_price)
        if filter_params.amenities:
            # Use PostgreSQL's array overlap operator for better performance
            query = query.filter(Project.amenities.overlap(filter_params.amenities))
        
        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.limit)
        
        return query.all()

    async def get_project(self, project_id: str, customer_id: str) -> Project:
        """Get a specific project."""
        project = self.db.query(Project).filter(
            Project.id == project_id,
            Project.customer_id == customer_id
        ).first()
        
        if not project:
            raise NotFoundError(detail="Project not found")
            
        return project

    async def create_project(
        self,
        project_in: ProjectCreate,
        customer_id: str,
        user_id: str
    ) -> Project:
        """Create a new project."""
        project = Project(
            **project_in.dict(exclude_unset=True),
            customer_id=customer_id,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        # Log audit
        self.audit_service.log_project_creation(
            project=project,
            user_id=user_id,
            customer_id=customer_id
        )
        
        return project

    async def update_project(
        self,
        project_id: str,
        project_in: ProjectUpdate,
        customer_id: str,
        user_id: str
    ) -> Project:
        """Update a project."""
        project = await self.get_project(project_id, customer_id)
        
        # Track changes for audit
        changes = {}
        for field, value in project_in.dict(exclude_unset=True).items():
            if getattr(project, field) != value:
                changes[field] = {
                    "old": getattr(project, field),
                    "new": value
                }
                setattr(project, field, value)
        
        project.updated_by = user_id
        from datetime import timezone
        project.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(project)
        
        # Log audit if there were changes
        if changes:
            self.audit_service.log_project_update(
                project=project,
                user_id=user_id,
                customer_id=customer_id,
                changes=changes
            )
        
        return project

    async def delete_project(
        self,
        project_id: str,
        customer_id: str,
        user_id: str
    ) -> bool:
        """Delete a project."""
        project = await self.get_project(project_id, customer_id)
        
        # Log audit before deletion
        self.audit_service.log_project_deletion(
            project=project,
            user_id=user_id,
            customer_id=customer_id
        )
        
        self.db.delete(project)
        self.db.commit()
        return True

async def add_feature(
         self,
         project_id: str,
         feature_in: ProjectFeatureCreate,
         customer_id: str,
         user_id: str
     ) -> ProjectFeature:
         """Add a feature to a project."""
         project = await self.get_project(project_id, customer_id)
         
        # Check for duplicate feature
        existing_feature = self.db.query(ProjectFeature).filter(
            ProjectFeature.project_id == project_id,
            ProjectFeature.name == feature_in.name
        ).first()
        
        if existing_feature:
            raise ValidationError(detail="Feature already exists for this project")
        
         feature = ProjectFeature(
             **feature_in.dict(),
             project_id=project_id
         )
        
        self.db.add(feature)
        self.db.commit()
        self.db.refresh(feature)
        
        # Log audit
        self.audit_service.log_project_feature_addition(
            project=project,
            feature=feature,
            user_id=user_id,
            customer_id=customer_id
        )
        
        return feature

    async def add_image(
        self,
        project_id: str,
        image_in: ProjectImageCreate,
        customer_id: str,
        user_id: str
    ) -> ProjectImage:
        """Add an image to a project."""
        project = await self.get_project(project_id, customer_id)
        
        image = ProjectImage(
            **image_in.dict(),
            project_id=project_id
        )
        
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        
        # Log audit
        self.audit_service.log_project_image_addition(
            project=project,
            image=image,
            user_id=user_id,
            customer_id=customer_id
        )
        
        return image

    async def add_amenity(
        self,
        project_id: str,
        amenity_in: ProjectAmenityCreate,
        customer_id: str,
        user_id: str
    ) -> ProjectAmenity:
        """Add an amenity to a project."""
        project = await self.get_project(project_id, customer_id)
        
        amenity = ProjectAmenity(
            **amenity_in.dict(),
            project_id=project_id
        )
        
        self.db.add(amenity)
        self.db.commit()
        self.db.refresh(amenity)
        
        # Log audit
        self.audit_service.log_project_amenity_addition(
            project=project,
            amenity=amenity,
            user_id=user_id,
            customer_id=customer_id
        )
        
        return amenity

    async def assign_lead(
        self,
        project_id: str,
        lead_in: ProjectLeadCreate,
        customer_id: str
    ) -> ProjectLead:
        """Assign a lead to a project."""
        project = await self.get_project(project_id, customer_id)
        
        # Check if lead is already assigned
        existing_assignment = self.db.query(ProjectLead).filter(
            ProjectLead.project_id == project_id,
            ProjectLead.lead_id == lead_in.lead_id
        ).first()
        
        if existing_assignment:
            raise ValidationError(detail="Lead is already assigned to this project")
        
        lead_assignment = ProjectLead(
            **lead_in.dict(),
            project_id=project_id
        )
        
        self.db.add(lead_assignment)
        self.db.commit()
        self.db.refresh(lead_assignment)
        
        # Log audit
        self.audit_service.log_project_lead_assignment(
            project=project,
            lead_assignment=lead_assignment,
            user_id=lead_in.assigned_by,
            customer_id=customer_id
        )
        
        return lead_assignment

    async def get_project_stats(self, customer_id: str) -> ProjectStats:
        """Get project statistics."""
        total_projects = self.db.query(func.count(Project.id)).filter(
            Project.customer_id == customer_id
        ).scalar()
        
        projects_by_type = dict(
            self.db.query(
                Project.type,
                func.count(Project.id)
            ).filter(
                Project.customer_id == customer_id
            ).group_by(Project.type).all()
        )
        
        projects_by_status = dict(
            self.db.query(
                Project.status,
                func.count(Project.id)
            ).filter(
                Project.customer_id == customer_id
            ).group_by(Project.status).all()
        )
        
        projects_by_city = dict(
            self.db.query(
                Project.city,
                func.count(Project.id)
            ).filter(
                Project.customer_id == customer_id
            ).group_by(Project.city).all()
        )
        
        total_value = self.db.query(func.sum(Project.total_value)).filter(
            Project.customer_id == customer_id
        ).scalar() or 0.0
        
        average_project_value = total_value / total_projects if total_projects > 0 else 0.0
        
        total_leads = self.db.query(func.count(ProjectLead.id)).join(
            Project
        ).filter(
            Project.customer_id == customer_id
        ).scalar()
        
        conversion_rate = 0.0  # Calculate based on your business logic
        
        return ProjectStats(
            total_projects=total_projects,
            projects_by_type=projects_by_type,
            projects_by_status=projects_by_status,
            projects_by_city=projects_by_city,
            total_value=total_value,
            average_project_value=average_project_value,
            total_leads=total_leads,
            conversion_rate=conversion_rate
        )

    async def get_project_analytics(self, customer_id: str) -> ProjectAnalytics:
        """Get project analytics."""
        # Lead trends (last 30 days)
        lead_trends = []
        for i in range(30):
            date = datetime.utcnow() - timedelta(days=i)
            count = self.db.query(func.count(ProjectLead.id)).join(
                Project
            ).filter(
                Project.customer_id == customer_id,
                func.date(ProjectLead.assigned_at) == date.date()
            ).scalar()
            lead_trends.append({
                "date": date.date().isoformat(),
                "count": count
            })
        
        # Status distribution
        status_distribution = self.db.query(
            Project.status,
            func.count(Project.id)
        ).filter(
            Project.customer_id == customer_id
        ).group_by(Project.status).all()
        
        # Value distribution
        value_ranges = [
            (0, 1000000),
            (1000000, 5000000),
            (5000000, 10000000),
            (10000000, float('inf'))
        ]
        value_distribution = []
        for min_val, max_val in value_ranges:
            count = self.db.query(func.count(Project.id)).filter(
                Project.customer_id == customer_id,
                Project.total_value >= min_val,
                Project.total_value < max_val
            ).scalar()
            value_distribution.append({
                "range": f"{min_val:,} - {max_val:,}",
                "count": count
            })
        
        # Location distribution
        location_distribution = self.db.query(
            Project.city,
            Project.state,
            func.count(Project.id)
        ).filter(
            Project.customer_id == customer_id
        ).group_by(Project.city, Project.state).all()
        
        # Amenity popularity
        amenity_popularity = []
        all_amenities = self.db.query(Project.amenities).filter(
            Project.customer_id == customer_id
        ).all()
amenity_counts = {}
         for amenities in all_amenities:
            if amenities[0]:  # Check if amenities exist
                for amenity in amenities[0]:
                 amenity_counts[amenity] = amenity_counts.get(amenity, 0) + 1
        for amenity, count in amenity_counts.items():
            amenity_popularity.append({
                "amenity": amenity,
                "count": count
            })
        
        return ProjectAnalytics(
            lead_trends=lead_trends,
            status_distribution=[{"status": s, "count": c} for s, c in status_distribution],
            value_distribution=value_distribution,
            location_distribution=[{"city": c, "state": s, "count": cnt} for c, s, cnt in location_distribution],
            amenity_popularity=amenity_popularity
        ) 