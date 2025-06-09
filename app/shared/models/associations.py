from sqlalchemy import Column, ForeignKey, String, Table

from app.shared.db.base_class import BaseModel

# Association table for project leads
project_leads = Table(
    'project_leads',
    BaseModel.metadata,
    Column('project_id', String(36), ForeignKey('projects.id'), primary_key=True),
    Column('lead_id', String(36), ForeignKey('leads.id'), primary_key=True)
)
