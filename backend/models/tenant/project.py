from sqlalchemy import Column, String, Integer, Text, Date, Index
from sqlalchemy.orm import relationship, validates
from models.base import AuditableBase

class Project(AuditableBase):
    """Project model for organizing work within a tenant"""
    __tablename__ = 'projects'

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Document date range (required)
    document_start_date = Column(Date, nullable=False, index=True)
    document_end_date = Column(Date, nullable=False, index=True)
    
    # Tenant ID (not a foreign key since tenant is in different database)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        # Ensure project name is unique within a tenant
        Index('ix_projects_tenant_name', 'tenant_id', 'name', unique=True),
        # Index for date range queries
        Index('ix_projects_tenant_date_range', 'tenant_id', 'document_start_date', 'document_end_date'),
    )
    
    # Relationships
    project_user_groups = relationship("ProjectUserGroup", back_populates="project")
    
    @validates('name')
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")
        if len(name.strip()) > 255:
            raise ValueError("Project name cannot exceed 255 characters")
        return name.strip()
    
    @validates('document_start_date')
    def validate_start_date(self, key, date):
        if date is None:
            raise ValueError("document_start_date cannot be null")
        return date
    
    @validates('document_end_date')
    def validate_end_date(self, key, end_date):
        if end_date is None:
            raise ValueError("document_end_date cannot be null")
        if hasattr(self, 'document_start_date') and self.document_start_date:
            if end_date <= self.document_start_date:
                raise ValueError("Document end date must be after start date")
        return end_date
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', tenant_id={self.tenant_id})>" 