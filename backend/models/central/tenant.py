from sqlalchemy import Column, String, Text
from sqlalchemy.orm import validates
from models.base import AuditableBase

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
        
        # Check for hyphens in slug
        if '-' in slug:
            raise ValueError("Slug cannot contain hyphens. Use underscores instead.")
        
        # Check for other invalid characters
        if not slug.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Slug can only contain letters, numbers, and underscores")
        
        return slug.strip().lower()
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, slug='{self.slug}', name='{self.name}')>" 