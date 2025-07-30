import json
from datetime import datetime
from typing import List
from models.central import Tenant
from .create_tenant import CreateTenantRequest, CreateTenantResponse
from .update_tenant import UpdateTenantRequest, UpdateTenantResponse
from .get_tenant import GetTenantResponse, TenantListItem, GetTenantsResponse

class TenantConverter:
    """Converter for transforming between Tenant models and DTOs"""
    
    @staticmethod
    def to_create_response(tenant: Tenant) -> CreateTenantResponse:
        """Convert Tenant model to CreateTenantResponse DTO"""
        # Convert JSON string back to dictionary
        metadata = None
        if tenant.tenant_metadata:
            try:
                metadata = json.loads(tenant.tenant_metadata)
            except (json.JSONDecodeError, TypeError):
                metadata = None
        
        return CreateTenantResponse(
            id=tenant.id,
            slug=tenant.slug,
            name=tenant.name,
            database_url=tenant.database_url,
            pinecone_index=tenant.pinecone_index,
            pinecone_region=tenant.pinecone_region,
            blob_storage_connection=tenant.blob_storage_connection,
            metadata=metadata,
            created_at=tenant.created_at.isoformat(),
            updated_at=tenant.updated_at.isoformat(),
            is_active=tenant.is_active
        )
    
    @staticmethod
    def to_update_response(tenant: Tenant) -> UpdateTenantResponse:
        """Convert Tenant model to UpdateTenantResponse DTO"""
        # Convert JSON string back to dictionary
        metadata = None
        if tenant.tenant_metadata:
            try:
                metadata = json.loads(tenant.tenant_metadata)
            except (json.JSONDecodeError, TypeError):
                metadata = None
        
        return UpdateTenantResponse(
            id=tenant.id,
            slug=tenant.slug,
            name=tenant.name,
            database_url=tenant.database_url,
            pinecone_index=tenant.pinecone_index,
            pinecone_region=tenant.pinecone_region,
            blob_storage_connection=tenant.blob_storage_connection,
            metadata=metadata,
            created_at=tenant.created_at.isoformat(),
            updated_at=tenant.updated_at.isoformat(),
            is_active=tenant.is_active
        )
    
    @staticmethod
    def to_get_response(tenant: Tenant) -> GetTenantResponse:
        """Convert Tenant model to GetTenantResponse DTO"""
        # Convert JSON string back to dictionary
        metadata = None
        if tenant.tenant_metadata:
            try:
                metadata = json.loads(tenant.tenant_metadata)
            except (json.JSONDecodeError, TypeError):
                metadata = None
        
        return GetTenantResponse(
            id=tenant.id,
            slug=tenant.slug,
            name=tenant.name,
            database_url=tenant.database_url,
            pinecone_index=tenant.pinecone_index,
            pinecone_region=tenant.pinecone_region,
            blob_storage_connection=tenant.blob_storage_connection,
            metadata=metadata,
            created_at=tenant.created_at.isoformat(),
            updated_at=tenant.updated_at.isoformat(),
            is_active=tenant.is_active
        )
    
    @staticmethod
    def to_list_item(tenant: Tenant) -> TenantListItem:
        """Convert Tenant model to TenantListItem DTO (simplified)"""
        return TenantListItem(
            id=tenant.id,
            slug=tenant.slug,
            name=tenant.name,
            created_at=tenant.created_at.isoformat(),
            is_active=tenant.is_active
        )
    
    @staticmethod
    def to_get_response_list(tenants: List[Tenant], total_count: int, page: int = None, page_size: int = None) -> GetTenantsResponse:
        """Convert list of Tenant models to GetTenantsResponse DTO"""
        tenant_items = [TenantConverter.to_list_item(tenant) for tenant in tenants]
        return GetTenantsResponse(
            tenants=tenant_items,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
    
    @staticmethod
    def from_create_request(dto: CreateTenantRequest) -> Tenant:
        """Convert CreateTenantRequest DTO to Tenant model"""
        return Tenant(
            slug=dto.slug,
            name=dto.name,
            database_url=dto.database_url,
            pinecone_index=dto.pinecone_index,
            pinecone_region=dto.pinecone_region,
            blob_storage_connection=dto.blob_storage_connection,
            tenant_metadata=json.dumps(dto.metadata) if dto.metadata else None
        )
    
    @staticmethod
    def from_update_request(tenant: Tenant, dto: UpdateTenantRequest) -> Tenant:
        """Update existing Tenant model with UpdateTenantRequest DTO data"""
        if dto.name is not None:
            tenant.name = dto.name
        if dto.database_url is not None:
            tenant.database_url = dto.database_url
        if dto.pinecone_index is not None:
            tenant.pinecone_index = dto.pinecone_index
        if dto.pinecone_region is not None:
            tenant.pinecone_region = dto.pinecone_region
        if dto.blob_storage_connection is not None:
            tenant.blob_storage_connection = dto.blob_storage_connection
        if dto.metadata is not None:
            tenant.tenant_metadata = json.dumps(dto.metadata)
        
        return tenant 