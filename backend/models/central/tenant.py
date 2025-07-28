from sqlalchemy import Column, String, Text
from sqlalchemy.orm import validates
from models.base import AuditableBase
import re

class Tenant(AuditableBase):
    """Central tenant model for storing tenant metadata and connection information"""
    __tablename__ = 'tenants'
    
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    
    # Connection strings for tenant-specific resources
    database_url = Column(String(500), nullable=True)  # Tenant-specific database
    pinecone_index = Column(String(100), nullable=True)  # Tenant-specific index name
    pinecone_region = Column(String(100), nullable=True)  # Tenant-specific region
    blob_storage_connection = Column(String(500), nullable=True)
    
    # Metadata field for additional tenant-specific data
    tenant_metadata = Column(Text, nullable=True)  # Store JSON as text for now
    
    @validates('slug')
    def validate_slug(self, key, slug):
        if not slug or not slug.strip():
            raise ValueError("Slug cannot be empty")
        
        slug = slug.strip().lower()
        
        # Check for valid characters (letters, numbers, hyphens, underscores)
        if not re.match(r'^[a-z0-9_-]+$', slug):
            raise ValueError("Slug can only contain letters, numbers, hyphens, and underscores")
        
        # Check length (considering Azure storage name limits)
        if len(slug) > 20:
            raise ValueError("Slug cannot be longer than 20 characters (to fit Azure storage naming)")
        
        if len(slug) < 3:
            raise ValueError("Slug must be at least 3 characters")
        
        # Check for consecutive hyphens or underscores
        if '--' in slug or '__' in slug:
            raise ValueError("Slug cannot contain consecutive hyphens or underscores")
        
        # Check for leading/trailing hyphens or underscores
        if slug.startswith('-') or slug.startswith('_') or slug.endswith('-') or slug.endswith('_'):
            raise ValueError("Slug cannot start or end with hyphens or underscores")
        
        return slug
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, slug='{self.slug}', name='{self.name}')>" 