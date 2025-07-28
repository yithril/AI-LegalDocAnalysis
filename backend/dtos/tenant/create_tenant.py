from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
import re

class CreateTenantRequest(BaseModel):
    """Request DTO for creating a new tenant"""
    
    slug: str = Field(
        ..., 
        min_length=3, 
        max_length=20,
        description="Unique tenant identifier (3-20 chars, lowercase letters, numbers, hyphens, underscores)"
    )
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Display name for the tenant"
    )
    database_url: Optional[str] = Field(
        None,
        max_length=500,
        description="Connection string for tenant-specific database"
    )
    pinecone_index: Optional[str] = Field(
        None,
        max_length=100,
        description="Pinecone index name for this tenant"
    )
    pinecone_region: Optional[str] = Field(
        None,
        max_length=100,
        description="Pinecone region for this tenant"
    )
    blob_storage_connection: Optional[str] = Field(
        None,
        max_length=500,
        description="Blob storage connection string for this tenant"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional tenant-specific metadata"
    )
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validate slug format: 3-20 chars, lowercase letters, numbers, hyphens, underscores"""
        v = v.strip().lower()
        
        if not re.match(r'^[a-z0-9_-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, hyphens, and underscores')
        
        # Check length (considering Azure storage name limits)
        if len(v) > 20:
            raise ValueError('Slug cannot be longer than 20 characters (to fit Azure storage naming)')
        
        if len(v) < 3:
            raise ValueError('Slug must be at least 3 characters')
        
        # Ensure it doesn't start or end with hyphen or underscore
        if v.startswith('-') or v.startswith('_') or v.endswith('-') or v.endswith('_'):
            raise ValueError('Slug cannot start or end with hyphens or underscores')
        
        # Ensure it doesn't have consecutive hyphens or underscores
        if '--' in v or '__' in v:
            raise ValueError('Slug cannot contain consecutive hyphens or underscores')
        
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate tenant name"""
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()

class CreateTenantResponse(BaseModel):
    """Response DTO for tenant creation"""
    
    id: int = Field(..., description="Unique tenant ID")
    slug: str = Field(..., description="Tenant slug")
    name: str = Field(..., description="Tenant display name")
    database_url: Optional[str] = Field(None, description="Database connection string")
    pinecone_index: Optional[str] = Field(None, description="Pinecone index name")
    pinecone_region: Optional[str] = Field(None, description="Pinecone region")
    blob_storage_connection: Optional[str] = Field(None, description="Blob storage connection")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Tenant metadata")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Active status") 