from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any

class UpdateTenantRequest(BaseModel):
    """Request DTO for updating an existing tenant"""
    
    name: Optional[str] = Field(
        None,
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
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate tenant name"""
        if v is not None:
            if not v.strip():
                raise ValueError('Name cannot be empty or whitespace only')
            return v.strip()
        return v
    
    @field_validator('metadata')
    @classmethod
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate metadata is not empty if provided"""
        if v is not None and not v:
            raise ValueError('Metadata cannot be an empty dictionary')
        return v

class UpdateTenantResponse(BaseModel):
    """Response DTO for tenant update"""
    
    id: int = Field(..., description="Unique tenant ID")
    slug: str = Field(..., description="Tenant slug (cannot be updated)")
    name: str = Field(..., description="Tenant display name")
    database_url: Optional[str] = Field(None, description="Database connection string")
    pinecone_index: Optional[str] = Field(None, description="Pinecone index name")
    pinecone_region: Optional[str] = Field(None, description="Pinecone region")
    blob_storage_connection: Optional[str] = Field(None, description="Blob storage connection")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Tenant metadata")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Active status") 