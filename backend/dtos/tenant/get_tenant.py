from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class GetTenantResponse(BaseModel):
    """Response DTO for getting a single tenant"""
    
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

class TenantListItem(BaseModel):
    """DTO for tenant list items (simplified version)"""
    
    id: int = Field(..., description="Unique tenant ID")
    slug: str = Field(..., description="Tenant slug")
    name: str = Field(..., description="Tenant display name")
    created_at: str = Field(..., description="Creation timestamp")
    is_active: bool = Field(..., description="Active status")

class GetTenantsResponse(BaseModel):
    """Response DTO for getting a list of tenants"""
    
    tenants: List[TenantListItem] = Field(..., description="List of tenants")
    total_count: int = Field(..., description="Total number of tenants")
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(None, description="Number of items per page") 