from sqlalchemy import Column, String, Integer, Index
from sqlalchemy.orm import relationship, validates
from models.base import AuditableBase

class UserGroup(AuditableBase):
    """User group model for organizing users within a tenant"""
    __tablename__ = 'user_groups'

    name = Column(String(255), nullable=False)
    
    # Tenant ID (not a foreign key since tenant is in different database)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Composite index for tenant + name (groups are unique per tenant)
    __table_args__ = (
        # Ensure group name is unique within a tenant
        Index('ix_user_groups_tenant_name', 'tenant_id', 'name', unique=True),
    )
    
    # Relationships
    users = relationship("UserUserGroup", back_populates="user_group")
    project_user_groups = relationship("ProjectUserGroup", back_populates="user_group")
    
    @validates('name')
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("User group name cannot be empty")
        if len(name.strip()) > 255:
            raise ValueError("User group name cannot exceed 255 characters")
        return name.strip()
    
    def __repr__(self):
        return f"<UserGroup(id={self.id}, name='{self.name}', tenant_id={self.tenant_id})>" 