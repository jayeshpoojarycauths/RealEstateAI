import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
from uuid import UUID

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.project.models.project import (
    Project,
    ProjectAmenity,
    ProjectFeature,
    ProjectImage,
    ProjectType,
    project_leads
)
from app.project.schemas.project import (
    ProjectAmenityCreate,
    ProjectAnalytics,
    ProjectCreate,
    ProjectFeatureCreate,
    ProjectFilter,
    ProjectImageCreate,
    ProjectLeadCreate,
    ProjectStats,
    ProjectUpdate
)
from app.shared.core.audit import AuditService
from app.shared.core.exceptions import NotFoundException, ValidationError, ValidationException
from app.shared.core.pagination import PaginationParams
from app.shared.services.ai import AIService
from app.shared.core.logging import logger

logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.audit_service = AuditService(db)

    async def list_projects(
        self,
        customer_id: str,
        filter_params: ProjectFilter,
        pagination: PaginationParams
    ) -> Tuple[List[Project], int]:
        """List projects with filtering and pagination."""
        query = self.db.query(Project).filter(Project.customer_id == customer_id)

        # Apply filters
        if filter_params.name:
            query = query.filter(Project.name.ilike(f"%{filter_params.name}%"))
        if filter_params.type:
            query = query.filter(Project.type == filter_params.type)
        if filter_params.status:
            query = query.filter(Project.status == filter_params.status)
        if filter_params.location:
            query = query.filter(Project.location.ilike(f"%{filter_params.location}%"))
        if filter_params.min_price:
            query = query.filter(Project.total_value >= filter_params.min_price)
        if filter_params.max_price:
            query = query.filter(Project.total_value <= filter_params.max_price)
        if filter_params.amenities:
            query = query.filter(Project.amenities.overlap(filter_params.amenities))

        # Get total count before pagination
        total_count = query.count()

        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.limit)

        return query.all(), total_count

    async def get_project(self, project_id: UUID, customer_id: UUID) -> Project:
        """Get a project by ID."""
        project = self.db.query(Project).filter(
            and_(
                Project.id == project_id,
                Project.customer_id == customer_id,
                Project.deleted_at.is_(None)
            )
        ).first()
        
        if not project:
            raise NotFoundException(f"Project {project_id} not found")
            
        return project

    async def create_project(
        self,
        project_data: ProjectCreate,
        customer_id: UUID,
        user_id: UUID
    ) -> Project:
        """Create a new project."""
        # Validate project type
        if not isinstance(project_data.type, ProjectType):
            raise ValidationError("Invalid project type")
            
        project = Project(
            **project_data.dict(),
            customer_id=customer_id,
            created_by=user_id,
            updated_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
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
        project_id: UUID,
        project_in: ProjectUpdate,
        customer_id: UUID
    ) -> Project:
        """Update a project."""
        project = await self.get_project(project_id, customer_id)
        
        # Validate update data
        if project_in.type and project_in.type not in ProjectType.__members__.values():
            raise ValidationException(f"Invalid project type: {project_in.type}")
        
        # Update project fields
        for field, value in project_in.dict(exclude_unset=True).items():
            setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(project)
        
        return project

    async def delete_project(
        self,
        project_id: UUID,
        customer_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a project."""
        # Verify project exists and belongs to customer
        await self.get_project(project_id, customer_id)
        
        # Log audit before deletion
        self.audit_service.log_project_deletion(
            project_id=project_id,
            user_id=user_id,
            customer_id=customer_id
        )
        
        # Soft delete
        self.db.query(Project).filter(
            Project.id == project_id,
            Project.customer_id == customer_id
        ).update({
            "deleted_at": datetime.utcnow(),
            "updated_by": user_id,
            "updated_at": datetime.utcnow()
        })
        
        self.db.commit()
        return True

    async def add_feature(
        self,
        project_id: UUID,
        feature_in: ProjectFeatureCreate,
        customer_id: UUID,
        user_id: UUID
    ) -> ProjectFeature:
        """Add a feature to a project."""
        project = await self.get_project(project_id, customer_id)
        
        # Validate feature data
        if not feature_in.name or not feature_in.value:
            raise ValidationException("Feature name and value are required")
        
        feature = ProjectFeature(
            project_id=project_id,
            name=feature_in.name,
            value=feature_in.value,
            description=feature_in.description,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(feature)
        self.db.commit()
        self.db.refresh(feature)
        
        return feature

    async def add_image(
        self,
        project_id: str,
        image_in: ProjectImageCreate,
        customer_id: str
    ) -> ProjectImage:
        """Add an image to a project."""
        # Verify project exists and belongs to customer
        await self.get_project(project_id, customer_id)
        
        image = ProjectImage(
            **image_in.dict(),
            project_id=project_id
        )
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        return image

    async def add_amenity(
        self,
        project_id: str,
        amenity_in: ProjectAmenityCreate,
        customer_id: str
    ) -> ProjectAmenity:
        """Add an amenity to a project."""
        # Verify project exists and belongs to customer
        await self.get_project(project_id, customer_id)
        
        # Check for duplicate amenity
        existing_amenity = self.db.query(ProjectAmenity).filter(
            ProjectAmenity.project_id == project_id,
            ProjectAmenity.name == amenity_in.name
        ).first()
        
        if existing_amenity:
            raise ValidationError(detail="Amenity already exists for this project")
            
        amenity = ProjectAmenity(
            **amenity_in.dict(),
            project_id=project_id
        )
        self.db.add(amenity)
        self.db.commit()
        self.db.refresh(amenity)
        return amenity

    async def assign_lead(
        self,
        project_id: UUID,
        lead_in: ProjectLeadCreate,
        customer_id: UUID
    ) -> Dict[str, Any]:
        """Assign a lead to a project using the association table."""
        # Verify project exists and belongs to customer
        project = await self.get_project(project_id, customer_id)
        
        try:
            # Insert into project_leads association table
            stmt = project_leads.insert().values(
                project_id=str(project_id),
                lead_id=str(lead_in.lead_id)
            )
            self.db.execute(stmt)
            self.db.commit()
            
            return {
                "message": "Lead assigned successfully",
                "project_id": str(project_id),
                "lead_id": str(lead_in.lead_id)
            }
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error assigning lead: {str(e)}")

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
        
        total_leads = self.db.query(func.count(project_leads.c.id)).join(
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
            count = self.db.query(func.count(project_leads.c.id)).join(
                Project
            ).filter(
                Project.customer_id == customer_id,
                func.date(project_leads.c.assigned_at) == date.date()
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